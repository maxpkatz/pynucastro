# unit tests for rates

from pytest import approx

import pynucastro as pyna


class TestTabularRates:
    @classmethod
    def setup_class(cls):
        """ this is run once for each class before any tests """

    @classmethod
    def teardown_class(cls):
        """ this is run once for each class after all tests """

    def setup_method(self):
        """ this is run before each test """

        lib_su = pyna.SuzukiLibrary()
        lib_la = pyna.LangankeLibrary()
        self.rc_su = pyna.RateCollection(libraries=[lib_su])
        self.rc_la = pyna.RateCollection(libraries=[lib_la])

    def teardown_method(self):
        """ this is run after each test """

    def test_rate_values_suzuki(self):

        rho = 1.2e8
        T = 1.5e9

        comp_su = pyna.Composition(self.rc_su.get_nuclei())
        comp_su.set_all(1)
        comp_su.normalize()

        # this is generated by doing
        # rvals = ec.evalue_rates(rho, T, comp)
        # for r in rvals:
        #     print(f"'{r.fname}': {rvals[r]},")

        stored_rates_su = {
            'al23__mg23': 0.003325571780147662,
            'al24__mg24': 0.0018609850628930817,
            'al25__mg25': 0.0008673916981132076,
            'al26__mg26': 1.6697474600870827e-05,
            'al27__mg27': 1.9145220125786163e-11,
            'al28__mg28': 1.7464898921832882e-13,
            'al28__si28': 4.758456199460916e-07,
            'f17__o17': 0.0009393387347391787,
            'f18__o18': 0.0002921538784067086,
            'f19__o19': 5.367481628599801e-17,
            'o19__f19':  1.277528299929593e-05,
            'f20__ne20': 4.267407547169812e-05,
            'f20__o20': 3.472915094339623e-14,
            'f21__ne21': 0.00010459838274932613,
            'f21__o21': 4.769850853548966e-28,
            'f22__ne22': 0.00011282658662092624,
            'f23__ne23': 0.00022270820344544705,
            'mg20__na20': 0.009212004716981132,
            'mg21__na21': 0.0049789164420485175,
            'mg22__na22': 0.0024188636363636365,
            'mg23__na23': 0.0007809339622641509,
            'mg24__na24': 1.0339819182389936e-20,
            'mg25__na25': 2.1270815094339622e-14,
            'mg26__na26': 2.284287373004354e-30,
            'mg27__al27': 5.7631558350803634e-09,
            'mg27__na27': 2.0061362683438153e-29,
            'mg28__al28': 3.286745956873315e-11,
            'mg28__na28': 5.5662931266846354e-45,
            'na19__ne19': 0.004455850049652432,
            'na20__ne20': 0.004357868867924529,
            'na21__ne21': 0.0007029830188679245,
            'na22__ne22': 1.9629150943396227e-06,
            'na23__ne23': 3.599119770303527e-16,
            'na24__mg24': 5.091114779874214e-07,
            'na24__ne24': 4.868698899371068e-11,
            'na25__mg25': 3.6938913207547163e-06,
            'na25__ne25': 3.969941886792453e-25,
            'na26__mg26': 0.001012000725689405,
            'na27__mg27': 0.0017497672955974842,
            'na28__mg28': 0.008824009433962263,
            'ne18__f18': 0.004117197064989518,
            'ne19__f19': 0.0013002313803376366,
            'ne20__f20': 9.132593396226415e-24,
            'ne21__f21': 1.4605112309074573e-19,
            'ne22__f22': 4.7896243567753e-37,
            'ne23__f23': 2.9241271534044295e-29,
            'ne23__na23': 8.229934372436421e-06,
            'ne24__na24': 4.895678459119496e-08,
            'ne25__na25': 0.0007466306415094339,
            'o17__f17': 1.5250188679245281e-22,
            'o18__f18': 3.5192620545073376e-23,
            'o20__f20': 8.06109716981132e-06,
            'o21__f21': 0.00010417529200359388,
            'p27__si27': 0.003163809923130678,
            'p28__si28': 0.002068931266846361,
            's28__p28': 0.004492893530997304,
            'si24__al24': 0.005087950471698113,
            'si25__al25': 0.003356480754716981,
            'si26__al26': 0.002266735123367199,
            'si27__al27': 0.000895324248777079,
            'si28__al28': 1.0828443396226414e-16,
        }

        ye_su = comp_su.eval_ye()
        ys_su = comp_su.get_molar()

        # the individual rate is
        # r = Y(reactant) * table_value

        for r in self.rc_su.get_rates():
            rr = ys_su[r.reactants[0]] * r.eval(T, rhoY=rho*ye_su)
            if r.fname in stored_rates_su:
                assert rr == approx(stored_rates_su[r.fname], rel=1.e-6, abs=1.e-100), f"rate: {r} does not agree"
            else:
                print(f"WARNING: missing Suzuki tests for tabular rate {r}")

    def test_rate_values_langanke(self):

        rho = 1.2e8
        T = 1.5e9

        comp_la = pyna.Composition(self.rc_la.get_nuclei())
        comp_la.set_all(1)
        comp_la.normalize()

        # this is generated by doing
        # rvals = ec.evalue_rates(rho, T, comp)
        # for r in rvals:
        #     print(f"'{r.fname}': {rvals[r]},")

        stored_rates_la = {
            'mn49__cr49': 5.976313549889056e-05,
            'mn55__fe55': 1.0870931655609214e-14,
            'co64__ni64': 0.00016049055573536534,
            'cr49__mn49': 1.4042142464499862e-37,
            'fe61__mn61': 2.071570032593256e-29,
            'fe57__co57': 2.586750842511416e-16,
            'fe54__co54': 1.7751526089164936e-38,
            'mn52__fe52': 9.519762446312908e-21,
            'cr57__mn57': 4.696286670271079e-06,
            'zn64__cu64': 1.3945994220820025e-09,
            'cu63__zn63': 1.2169953124084304e-23,
            'co63__fe63': 9.105187750090365e-28,
            'ca51__sc51': 1.4456370787113852e-05,
            'mn56__fe56': 3.4708946171269053e-07,
            'zn63__cu63': 3.2907046540680336e-07,
            'sc47__ca47': 2.0918550937696197e-15,
            'mn54__fe54': 5.42295118415859e-13,
            'v54__ti54': 4.448726378749731e-21,
            'co58__fe58': 1.9417864281459944e-09,
            'ni63__cu63': 9.446891022076792e-13,
            'ca48__sc48': 7.52295072999418e-20,
            'v56__ti56': 5.7868393754633324e-30,
            'fe60__co60': 1.3598099181567122e-13,
            'ga64__zn64': 2.3629225173155347e-06,
            'fe57__mn57': 1.1085482461950966e-15,
            'mn50__cr50': 2.6709112080483608e-05,
            'fe56__mn56': 1.4237752129795872e-18,
            'ge65__ga65': 5.724217120210809e-06,
            'ni59__co59': 6.741824503998823e-09,
            'ca47__sc47': 4.6294734412831486e-11,
            'ti51__v51': 2.0001348583000549e-07,
            'cu65__zn65': 5.101713878469135e-17,
            'zn64__ga64': 2.6696202067514447e-35,
            'co64__fe64': 3.376365709422004e-22,
            'ca46__sc46': 1.2355821432244698e-18,
            'sc48__ca48': 1.3976171381618535e-14,
            'v51__cr51': 2.600514494725662e-16,
            'sc52__ti52': 1.2434436569304634e-05,
            'ni58__cu58': 2.5656739300320643e-39,
            'co57__ni57': 7.042949902577483e-23,
            'ti55__v55': 6.328004296897341e-05,
            'ge64__ga64': 3.966883816581594e-06,
            'zn61__cu61': 1.9244189281397437e-06,
            'co62__fe62': 3.992434183427976e-16,
            'cr58__mn58': 1.2858830193823727e-05,
            'ti50__v50': 1.5054261322236473e-19,
            'co61__fe61': 1.8633722342877252e-20,
            'ni65__cu65': 5.220548060458926e-08,
            'ti56__v56': 0.0004329536725078675,
            'v55__cr55': 1.4800172095979908e-05,
            'ti47__v47': 4.482616619344033e-22,
            'cu58__ni58': 1.4328524193362064e-05,
            'sc46__ti46': 3.5064820754593184e-10,
            'co65__ni65': 6.290948041291289e-05,
            'ca50__sc50': 6.466353615938299e-06,
            'zn62__ga62': 6.534882232148034e-42,
            'co54__fe54': 2.00556016547461e-05,
            'fe63__co63': 1.3252228191272648e-05,
            'cr50__mn50': 1.1341211525008128e-36,
            'ni61__co61': 7.678910749048194e-12,
            'v49__cr49': 2.015734712943605e-21,
            'co63__ni63': 2.839807523497643e-06,
            'v47__ti47': 6.990875967911692e-07,
            'fe52__mn52': 4.07968011090249e-07,
            'mn59__fe59': 1.3297727934583521e-05,
            'mn60__fe60': 0.0002867333471983723,
            'v47__cr47': 4.672309431630382e-37,
            'mn57__cr57': 1.444623246753005e-23,
            'mn61__fe61': 0.00028333460478183176,
            'ti46__v46': 1.249889510136282e-35,
            'sc49__ti49': 2.0532100192061002e-08,
            'v51__ti51': 1.633274865627644e-15,
            'co60__ni60': 3.2997284747922698e-09,
            'ti53__v53': 2.0387012316051957e-06,
            'co55__fe55': 7.083807736689796e-08,
            'mn58__fe58': 9.664991163970471e-06,
            'co56__ni56': 2.335831053749306e-19,
            'mn56__cr56': 3.2541789230617425e-13,
            'v53__cr53': 1.2143771456331842e-06,
            'ni65__co65': 8.505818243110729e-26,
            'fe59__co59': 5.379940136684123e-10,
            'ni61__cu61': 1.2773197281030268e-20,
            'cr51__v51': 2.5296432551361395e-08,
            'mn55__cr55': 3.9560954861874263e-16,
            'mn58__cr58': 1.2711636381772529e-20,
            'v45__cr45': 5.028250912705287e-54,
            'cu61__zn61': 3.344256808182233e-30,
            'ca45__sc45': 1.0078988301091122e-13,
            'ti49__sc49': 1.3977624680385004e-14,
            'co61__ni61': 4.418751920249911e-09,
            'v46__ti46': 6.135806048464205e-05,
            'ni62__cu62': 2.839473143625473e-25,
            'ti51__sc51': 1.0941056954308053e-27,
            'fe53__mn53': 1.050397272267103e-06,
            'zn60__cu60': 2.0392863134253426e-06,
            'mn57__fe57': 6.190911549277483e-07,
            'sc45__ca45': 5.36311292006398e-10,
            'mn60__cr60': 9.538458719350535e-27,
            'cr54__mn54': 8.876376093127288e-17,
            'sc49__ca49': 5.746896489043991e-25,
            'v53__ti53': 1.426768739178871e-23,
            'ga63__zn63': 5.167600188795752e-06,
            'cr55__v55': 1.1621622528125028e-25,
            'v45__ti45': 5.1099534174626495e-05,
            'v49__ti49': 2.3037395321069294e-09,
            'sc50__ca50': 8.563660674843281e-24,
            'fe64__co64': 5.1457594572713654e-05,
            'fe55__mn55': 1.991896485718447e-09,
            'co55__ni55': 1.463075592693622e-40,
            'zn65__cu65': 1.1474033096027321e-08,
            'sc51__ti51': 8.166938379237046e-06,
            'cr60__mn60': 0.00021601216241988547,
            'co60__fe60': 4.231342737687033e-12,
            'ga65__ge65': 5.172685788150672e-33,
            'cu64__zn64': 1.619755565639683e-11,
            'fe60__mn60': 4.116026900933871e-33,
            'cr52__v52': 3.2406051007329356e-19,
            'cr48__v48': 6.892681604998934e-07,
            'ti48__v48': 4.230466082846648e-25,
            'cr56__v56': 5.277660236034153e-35,
            'fe56__co56': 8.860157210539753e-27,
            'v52__ti52': 2.6830335988380486e-14,
            'co59__fe59': 2.2375741866695853e-14,
            'ti46__sc46': 1.0736719895948243e-15,
            'mn53__cr53': 6.844686876533021e-10,
            'zn65__ga65': 1.2639098494253299e-23,
            'v50__ti50': 4.90523084525967e-10,
            'cr54__v54': 6.098677875284561e-29,
            'v50__cr50': 1.1766829226998693e-10,
            'sc50__ti50': 1.3294115589315598e-06,
            'ni55__co55': 7.731553499471018e-05,
            'cr55__mn55': 3.298122371393117e-07,
            'fe59__mn59': 2.1967338551174844e-23,
            'mn53__fe53': 1.7553090229831206e-24,
            'sc45__ti45': 9.895026032318715e-20,
            'cr47__v47': 6.0329759904074444e-05,
            'cr46__v46': 0.0001339280739525003,
            'ti54__v54': 4.142244167055341e-06,
            'fe58__co58': 1.2537226192145582e-19,
            'cr52__mn52': 4.5250784333399746e-27,
            'cr51__mn51': 6.547255343673247e-23,
            'ti50__sc50': 7.955352914718596e-29,
            'mn54__cr54': 1.812323388049544e-09,
            'cr58__v58': 7.181273402432556e-43,
            'ni57__co57': 1.0369423195572108e-07,
            'v48__ti48': 1.514914831550926e-07,
            'co57__fe57': 1.9442611543524594e-09,
            'cu61__ni61': 4.637667621991208e-07,
            'co58__ni58': 1.4729956398875682e-13,
            'ni60__cu60': 6.990016557872739e-32,
            'ga62__zn62': 8.26490308544106e-05,
            'cr53__v53': 1.1100782289621385e-17,
            'zn62__cu62': 5.155107966275718e-07,
            'ti47__sc47': 3.495679413696456e-10,
            'ni62__co62': 1.775161071264576e-23,
            'fe58__mn58': 3.0775240911819687e-26,
            'ni60__co60': 3.55204291753771e-17,
            'co62__ni62': 9.643568404169445e-07,
            'cu59__ni59': 2.263484074617255e-06,
            'ga64__ge64': 3.0091891060049905e-28,
            'sc48__ti48': 1.239904446647579e-09,
            'ti52__v52': 5.80264646398903e-07,
            'v52__cr52': 4.1843317642366963e-07,
            'zn63__ga63': 2.302973313356947e-31,
            'cu63__ni63': 1.035831002704801e-09,
            'v57__cr57': 0.00031315157419044564,
            'cr59__mn59': 0.00012582804333434919,
            'cu60__zn60': 2.854159271365958e-26,
            'ni64__co64': 1.6536724109168202e-29,
            'co59__ni59': 6.946682395373553e-17,
            'sc51__ca51': 1.1509574775260463e-30,
            'cr45__v45': 0.0003008963649035491,
            'cu62__ni62': 2.8264269495889643e-07,
            'fe61__co61': 5.003796279538818e-07,
            'ti45__v45': 6.924954768952397e-36,
            'ti45__sc45': 5.693993159987009e-07,
            'mn59__cr59': 9.073554313934933e-32,
            'v46__cr46': 2.253572960889994e-37,
            'cr56__mn56': 1.0925502679484554e-07,
            'cr49__v49': 8.718331430454943e-07,
            'ni64__cu64': 5.086856435845813e-18,
            'sc47__ti47': 1.4911852421792674e-11,
            'fe55__co55': 3.795480507785559e-23,
            'cu64__ni64': 9.108554912662637e-08,
            'ti49__v49': 9.827281010503801e-15,
            'fe54__mn54': 5.107821302810202e-13,
            'ti52__sc52': 3.996005812300032e-35,
            'ti48__sc48': 2.814415523139798e-20,
            'cr53__mn53': 4.746282514290935e-15,
            'ni56__co56': 1.2955119635349347e-07,
            'cu62__zn62': 3.6748343343890065e-19,
            'ni59__cu59': 2.5280021748766108e-28,
            'ca49__sc49': 1.3534224461147526e-07,
            'v55__ti55': 6.702962124426423e-31,
            'mn52__cr52': 5.9241508850831537e-08,
            'v58__cr58': 0.0006594797449714386,
            'v56__cr56': 0.0002309093016779652,
            'co56__fe56': 1.5046705742612305e-08,
            'v54__cr54': 5.0261528882085374e-06,
            'mn51__cr51': 3.048311038758152e-07,
            'cu65__ni65': 3.8611448842104754e-14,
            'cr57__v57': 3.2942351677607236e-32,
            'fe62__co62': 8.245894335831766e-07,
            'ni58__co58': 2.9322531487685562e-12,
            'cr50__v50': 9.742254050234834e-12,
            'cu60__ni60': 8.403848304917242e-07,
            'ni63__co63': 9.063353212442658e-19,
            'sc46__ca46': 2.1177350434065018e-10,
            'v48__cr48': 5.799468815353305e-19,
            'ga65__zn65': 8.048521309454472e-07,
        }

        ye_la = comp_la.eval_ye()
        ys_la = comp_la.get_molar()

        # the individual rate is
        # r = Y(reactant) * table_value

        for r in self.rc_la.get_rates():
            rr = ys_la[r.reactants[0]] * r.eval(T, rhoY=rho*ye_la)
            if r.fname in stored_rates_la:
                assert rr == approx(stored_rates_la[r.fname], rel=1.e-6, abs=1.e-100), f"rate: {r} does not agree"
            else:
                print(f"WARNING: missing Langanke tests for tabular rate {r}")
