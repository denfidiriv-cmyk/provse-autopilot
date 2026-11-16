from mk import mk, B
s = B("swiss")
mk("c4", "swiss", [
 s("До", "chapter", no="СПРАВА №4", text="УГОДА З NESTLÉ"),
 s("пюре", "video", vid="warehouse_3.mp4", kicker="пюре, приправи, соуси"),
 s("Річний", "big", text="$100 МЛН+", acc=["МЛН+"], size=220, count=[0, 100, "$#"], cdur=1.2, sub="річний виторг Технокому"),
 s("з'являється", "video", vid="handshake_2.mp4", tag="ПОКУПЕЦЬ", tr="cut"),
 s("Швейцарський", "photo", img="p25.jpg", tag="NESTLÉ, ВЕВЕ"),
 s("дві", "big", text="$150 МЛН", acc=["МЛН"], size=230, count=[0, 150, "$#"], cdur=1.3, sub="2010 рік: Nestlé купує Техноком"),
 s("Для", "video", vid="switz_1.mp4", text="ПЕРЕМОГА", acc=["ПЕРЕМОГА"], size=170, tr="cut"),
 s("Але", "video", vid="money_2.mp4", kicker="але не на пенсію"),
 s("Гроші", "video", vid="vietnam_1.mp4", tag="ДОДОМУ, У В'ЄТНАМ", tr="cut"),
], [[0, "Audionautix-com-ccby-bigswingband.mp3", 0, 1.0]])
