#ifndef TABLE_RATES_H
#define TABLE_RATES_H

#include <iostream>
#include <sstream>
#include <fstream>
#include <string>

#include <AMReX_Array.H>

using namespace amrex;

void init_tabular();

// Table is expected to be in terms of dens*ye and temp (non-logarithmic, cgs units)
// Table energy units are expected in terms of ergs

// all tables are expected to have columns:
// rhoY     T   mu    dQ    Vs    e-cap-rate   nu-energy-loss  gamma-energy
// g/cm^3   K   erg   erg   erg   1/s          erg/s           erg/s
//

const int num_tables = 0;

enum TableVars
{
    jtab_mu      = 1,
    jtab_dq      = 2,
    jtab_vs      = 3,
    jtab_rate    = 4,
    jtab_nuloss  = 5,
    jtab_gamma   = 6,
    num_vars = jtab_gamma
};


struct table_t
{
    int ntemp;
    int nrhoy;
    int nvars;
    int nheader;
};

// we add a 7th quantity dr/dT
// k_drate_dt is used only for calculating the derivative
// of rate with temperature from the table, it isn't an index
// into the table but into the 'entries' array in, eg. get_entries.

const int k_drate_dt   = 7;
const int add_vars     = 1;  // 1 Additional Var in entries


namespace rate_tables
{
}

template <typename R, typename T, typename D>
void init_tab_info(const table_t& tf, const std::string& file, R& rhoy, T& temp, D& data) {

    std::ifstream table;
    table.open(file);

    std::string line;

    // read and skip over the header

    for (int i = 0; i < tf.nheader; ++i) {
        std::getline(table, line);
    }

    // now the data -- there are 2 extra columns, for temp and rhoy

    for (int j = 1; j <= tf.nrhoy; ++j) {
        for (int i = 1; i <= tf.ntemp; ++i) {
            std::getline(table, line);
            std::istringstream sdata(line);

            sdata >> rhoy(j) >> temp(i);

            for (int n = 1; n <= tf.nvars; ++n) {
                sdata >> data(i, j, n);
            }
        }
    }

    for (int j = 1; j <= tf.nrhoy; ++j) {
        for (int i = 1; i <= tf.ntemp; ++i) {

            if (1 == i) {
                rhoy(j) = std::pow(10.0_rt, rhoy(j));
            }

            if (1 == j) {
                if (temp(i) > 33.0_rt){
                    amrex::Error("init_tab_info: Table data needs to be updated");
                }

                temp(i) = std::pow(10.0_rt, temp(i));
            }

            data(i, j, jtab_rate) = std::pow(10.0_rt, data(i, j, jtab_rate));
            data(i, j, jtab_nuloss) = std::pow(10.0_rt, data(i, j, jtab_nuloss));
            data(i, j, jtab_gamma) = std::pow(10.0_rt, data(i, j, jtab_gamma));
        }
    }

    table.close();
}


template <typename V>
AMREX_GPU_HOST_DEVICE AMREX_INLINE
int vector_index_lu(const int vlen, const V& vector, const Real fvar)
{

    // Returns the greatest index of vector for which vector(index) < fvar.
    // Return 1 if fvar < vector(1)
    // Return size(vector)-1 if fvar > vector(size(vector))
    // The interval [index, index+1] brackets fvar for fvar within the range of vector.

    int index;

    if (fvar < vector(1)) {
        index = 1;
    } else if (fvar > vector(vlen)) {
        index = vlen - 1;
    } else {
        int nup = vlen;
        int ndn = 1;
        for (int i = 1; i <= vlen; ++i) {
            int j = ndn + (nup - ndn)/2;
            if (fvar < vector(j)) {
                nup = j;
            } else {
                ndn = j;
            }
            if ((nup - ndn) == 1) {
                break;
            }
        }
        index = ndn;
    }

    return index;
}


AMREX_INLINE AMREX_GPU_HOST_DEVICE
Real
bl_clamp(const Real xlo, const Real xhi, const Real flo, const Real fhi, const Real x)
{

    // Perform bilinear interpolation within the interval [xlo, xhi]
    // where the function values at the endpoints are defined by:
    // flo = f(xlo)
    // fhi = f(xhi)
    // Returns f(x), the values flo and fhi interpolated at x
    // f(x) = flo if x <= xlo
    // f(x) = fhi if x >= xhi

    Real f;
    if (x <= xlo) {
        f = flo;
    } else if (x >= xhi ) {
        f = fhi;
    } else {
        f = (flo * (xhi - x) + fhi * (x - xlo) ) / (xhi - xlo);
    }

    return f;
}

AMREX_INLINE AMREX_GPU_HOST_DEVICE
Real
bl_extrap(const Real xlo, const Real xhi, const Real flo, const Real fhi, const Real x)
{

    // Perform bilinear interpolation within the interval [xlo, xhi]
    // where the function values at the endpoints are defined by:
    // flo = f(xlo)
    // fhi = f(xhi)
    // Returns f(x), the values flo and fhi interpolated at x
    // If x <= xlo or x >= xhi, f(x) is extrapolated at x

    Real f = (flo * (xhi - x) + fhi * (x - xlo) ) / (xhi - xlo);

    return f;
}


template <typename R, typename T, typename D>
AMREX_INLINE AMREX_GPU_HOST_DEVICE
void
get_entries(const table_t& table_meta,
            const R& rhoy_table, const T& temp_table, const D& data,
            const Real rhoy, const Real temp, Array1D<Real, 1, num_vars+1>& entries)
{


    // The last element of entries is the derivative of rate with temperature
    // drate_dt, evaluated by central differencing at the box corners
    // and then performing a bilinear interpolation on those central differences.


    // Get box-corner points for interpolation
    // This deals with out-of-range inputs via linear extrapolation

    int irhoy_lo = vector_index_lu(table_meta.nrhoy, rhoy_table, rhoy);
    int itemp_lo = vector_index_lu(table_meta.ntemp, temp_table, temp);

    int irhoy_hi = irhoy_lo + 1;
    int itemp_hi = itemp_lo + 1;

    // Bilinear interpolation within the box
    // The desired point is denoted by ABCD, within the box.
    // The value of ivar at ABCD is denoted by fvar.
    // T ^   B .      . C
    //   |
    //   |  AB   ABCD   CD
    //   |     .      .
    //   |   A          D
    //   |___________________> rho*Ye

    Real temp_lo = temp_table(itemp_lo);
    Real temp_hi = temp_table(itemp_hi);
    Real rhoy_lo = rhoy_table(irhoy_lo);
    Real rhoy_hi = rhoy_table(irhoy_hi);

    // Interpolate for each table entry

    for (int ivar = 1; ivar <= num_vars; ivar++) {
        Real f_i = bl_extrap(temp_lo, temp_hi,
                             data(itemp_lo, irhoy_lo, ivar),
                             data(itemp_hi, irhoy_lo, ivar),
                             temp);

        Real f_ip1 = bl_extrap(temp_lo, temp_hi,
                               data(itemp_lo, irhoy_hi, ivar),
                               data(itemp_hi, irhoy_hi, ivar),
                               temp);

        // NOLINTNEXTLINE(readability-suspicious-call-argument)
        entries(ivar) = bl_extrap(rhoy_lo, rhoy_hi, f_i, f_ip1, rhoy);
    }

    // Calculate the derivative of rate with temperature, d(rate)/d(t)
    // (Clamp interpolations in rhoy to avoid unphysical temperature derivatives)

    if ((itemp_lo - 1 < 1) || (itemp_hi + 1 > table_meta.ntemp)) {
        // We're at the first or last table cell (in temperature)
        // First do bilinear interpolation in rhoy for the table at tlo and thi

        Real f_i = bl_clamp(rhoy_lo, rhoy_hi,
                            data(itemp_lo, irhoy_lo, jtab_rate),
                            data(itemp_lo, irhoy_hi, jtab_rate),
                            rhoy);

        Real f_ip1 = bl_clamp(rhoy_lo, rhoy_hi,
                              data(itemp_hi, irhoy_lo, jtab_rate),
                              data(itemp_hi, irhoy_hi, jtab_rate),
                              rhoy);

        // Approximate d(rate)/d(t) via forward differencing

        entries(k_drate_dt) = (f_ip1 - f_i) / (temp_hi - temp_lo);

    } else {
        // Approximate d(rate)/d(t) via bilinear interpolation on central differences

        Real t_im1 = temp_table(itemp_lo-1);
        Real t_i   = temp_table(itemp_lo);
        Real t_ip1 = temp_table(itemp_hi);
        Real t_ip2 = temp_table(itemp_hi+1);

        Real f_im1 = bl_clamp(rhoy_lo, rhoy_hi,
                              data(itemp_lo-1, irhoy_lo, jtab_rate),
                              data(itemp_lo-1, irhoy_hi, jtab_rate),
                              rhoy);

        Real f_i = bl_clamp(rhoy_lo, rhoy_hi,
                            data(itemp_lo, irhoy_lo, jtab_rate),
                            data(itemp_lo, irhoy_hi, jtab_rate ),
                            rhoy);

        Real f_ip1 = bl_clamp(rhoy_lo, rhoy_hi,
                              data(itemp_hi, irhoy_lo, jtab_rate),
                              data(itemp_hi, irhoy_hi, jtab_rate ),
                              rhoy);

        Real f_ip2 = bl_clamp(rhoy_lo, rhoy_hi,
                              data(itemp_hi+1, irhoy_lo, jtab_rate ),
                              data(itemp_hi+1, irhoy_hi, jtab_rate ),
                              rhoy);

        // Get central difference derivatives at the box corners

        Real drdt_i   = (f_ip1 - f_im1) / (t_ip1 - t_im1);
        Real drdt_ip1 = (f_ip2 - f_i)   / (t_ip2 - t_i);

        // Interpolate in temperature
        // (Since we're inside the table in temp, use bl_extrap, it's faster)

        entries(k_drate_dt) = bl_extrap(t_i, t_ip1, drdt_i, drdt_ip1, temp);

    }
}


template <typename R, typename T, typename D>
AMREX_INLINE AMREX_GPU_HOST_DEVICE
void
tabular_evaluate(const table_t& table_meta,
                 const R& rhoy_table, const T& temp_table, const D& data,
                 const Real rhoy, const Real temp,
                 Real& rate, Real& drate_dt, Real& edot_nu, Real& edot_gamma)
{


    Array1D<Real, 1, num_vars+1> entries;

    // Get the table entries at this rhoy, temp

    get_entries(table_meta, rhoy_table, temp_table, data,
                rhoy, temp, entries);

    // Fill outputs: rate, d(rate)/d(temperature), and
    // (negative) neutrino loss contribution to energy generation

    rate       = entries(jtab_rate);
    drate_dt   = entries(k_drate_dt);
    edot_nu    = -entries(jtab_nuloss);
    edot_gamma = entries(jtab_gamma);
}

#endif
