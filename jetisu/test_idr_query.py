from jetisu.idr_query import idr_query


def test_idr_query1():
    res = idr_query("""

    select duty from ACT_Conveyance_Duty where price = 1200000 and eligible_owner_occupier;

    """, True)
    assert res == (('duty',), [(47590,)])


def test_idr_query2():
    res = idr_query("""

    select eligible_owner_occupier, duty
    from ACT_Conveyance_Duty
    where price = 1200000 and non_commercial;

    """, True)
    assert res == (('eligible_owner_occupier', 'duty'), [(True, 47590), (False, 49750)])


def test_idr_query3():
    res = idr_query("""

    select * from ACT_Conveyance_Duty where price = 1200000;

    """, True)
    assert res == (('non_commercial', 'eligible_owner_occupier', 'duty', 'price'),
                   [(True, True, 47590, 1200000.0), (True, False, 49750, 1200000.0), (False, False, 0, 1200000.0)])


def test_idr_query4():
    res = idr_query("""

    select * from ACT_Conveyance_Duty where price = 2000000;

    """, True)
    assert res == (('non_commercial', 'eligible_owner_occupier', 'duty', 'price'),
                   [(True, True, 90800, 2000000.0), (True, False, 90800, 2000000.0), (False, False, 100000, 2000000.0)])


def test_idr_query5():
    res = idr_query("""

    select price from ACT_Conveyance_Duty where duty = 50150 and eligible_owner_occupier;

    """, True)
    assert res == (('price',),
                   [(1240000,), (1239999,), (1239998,), (1239997,), (1239996,), (1239995,), (1239994,), (1239993,),
                    (1239992,), (1239991,), (1239990,), (1239989,), (1239988,), (1239987,), (1239986,), (1239985,),
                    (1239984,), (1239983,), (1239982,), (1239981,), (1239980,), (1239979,), (1239978,), (1239977,),
                    (1239976,), (1239975,), (1239974,), (1239973,), (1239972,), (1239971,), (1239970,), (1239969,),
                    (1239968,), (1239967,), (1239966,), (1239965,), (1239964,), (1239963,), (1239962,), (1239961,),
                    (1239960,), (1239959,), (1239958,), (1239957,), (1239956,), (1239955,), (1239954,), (1239953,),
                    (1239952,), (1239951,), (1239950,), (1239949,), (1239948,), (1239947,), (1239946,), (1239945,),
                    (1239944,), (1239943,), (1239942,), (1239941,), (1239940,), (1239939,), (1239938,), (1239937,),
                    (1239936,), (1239935,), (1239934,), (1239933,), (1239932,), (1239931,), (1239930,), (1239929,),
                    (1239928,), (1239927,), (1239926,), (1239925,), (1239924,), (1239923,), (1239922,), (1239921,),
                    (1239920,), (1239919,), (1239918,), (1239917,), (1239916,), (1239915,), (1239914,), (1239913,),
                    (1239912,), (1239911,), (1239910,), (1239909,), (1239908,), (1239907,), (1239906,), (1239905,),
                    (1239904,), (1239903,), (1239902,), (1239901,)])


def test_idr_query6():
    res = idr_query("""

    select non_commercial, 
    eligible_owner_occupier, 
    min(price) min_price, 
    max(price) max_price 
from ACT_Conveyance_Duty 
    where duty = 140740 
    group by non_commercial, eligible_owner_occupier;

    """, True)
    assert res == (('non_commercial', 'eligible_owner_occupier', 'min_price', 'max_price'),
                   [(False, False, 2814701, 2814800), (True, False, 3099901, 3100000), (True, True, 3099901, 3100000)])
