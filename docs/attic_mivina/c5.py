from mk import mk, B
v = B("viet")
mk("c5", "viet", [
 v("Ще", "chapter", no="СПРАВА №5", text="ВІД ЛОКШИНИ ДО ЕЛЕКТРОКАРІВ"),
 v("острів", "video", vid="beach_2.mp4", kicker="острів біля узбережжя В'єтнаму"),
 v("курорт", "photo", img="p20.jpg", tag="VINPEARL, НЯЧАНГ", tr="cut"),
 v("вежі", "photo", img="p23.jpg", tag="LANDMARK 81", kicker="вежі, торгові центри, квартали", pos="50% 30%"),
 v("Усе", "polaroid", img="p01.png", w=700, h=470, rot=-4, cap="Vingroup"),
 v("тисячі", "big", text="ПЕРШИЙ МІЛЬЯРДЕР", acc=["МІЛЬЯРДЕР"], size=170, sub="В'єтнаму, за Forbes, 2013", tr="flash"),
 v("далі", "video", vid="evdrive_3.mp4", text="БОЖЕВІЛЛЯ?", acc=["БОЖЕВІЛЛЯ?"], size=170, freeze="божевіллям:"),
 v("запускає", "photo", img="p17.jpg", tag="VINFAST", tr="cut"),
 v("Компанія", "video", vid="ev_1.mp4", kicker="електромобілі й електроскутери"),
 v("двадцять", "photo", img="p15.jpg", tag="NASDAQ, 2023", tr="cut"),
 v("акції", "big", text="$10 → $93", acc=["$93"], size=220, sub="акції VinFast після виходу на біржу"),
 v("компанію", "big", text="≈$200 МЛРД", acc=["МЛРД"], size=210, sub="дорожче за Ford і General Motors", tr="cut"),
 v("Потім", "video", vid="stock_1.mp4", kicker="акції падають"),
 v("За", "big", text="$34 МЛРД", acc=["МЛРД"], size=230, count=[0, 34, "$#"], cdur=1.2, sub="статок Вионга, Forbes, весна 2026"),
 v("все", "photo", img="p07.jpg", tag="З ХАРКІВСЬКОЇ ЛОКШИНИ", tr="cut"),
], [[0, "Epic_Trailer_by_Rafael_Krux.ogg", 0, 1.0], [12, "Ouroboros_%28ISRC_USUAN1400007%29.mp3", 0, 1.0]])
