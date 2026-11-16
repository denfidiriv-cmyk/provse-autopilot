from mk import mk, B
k = B("kharkiv90")
mk("c1", "kharkiv90", [
 k("Фам", "chapter", no="СПРАВА №1", text="ХАРКІВ, 90-ТІ"),
 k("В'єтнамі,", "photo", img="p21.jpg", tag="В'ЄТНАМ, 1968"),
 k("математику,", "video", vid="lecture_1.mp4", kicker="стипендія за математику", tr="cut"),
 k("Москву,", "photo", img="p14.jpg", kicker="геологорозвідувальний інститут"),
 k("копалини.", "video", vid="geology_1.mp4", text="ШУКАТИ КОПАЛИНИ", acc=["КОПАЛИНИ"], size=140, tr="cut"),
 k("Союз", "video", vid="oldtv_3.mp4", text="СОЮЗ РОЗВАЛЮЄТЬСЯ", acc=["РОЗВАЛЮЄТЬСЯ"], size=140),
 k("переїжджає", "photo", img="p03.jpg", tag="ХАРКІВ", punch=["Харків."], tr="cut"),
 k("гроші", "video", vid="calc_3.mp4", text="ГРОШІ ЗНЕЦІНЮЮТЬСЯ", acc=["ЗНЕЦІНЮЮТЬСЯ"], size=130),
 k("ринках", "video", vid="shelf_2.mp4", kicker="від джинсів до запчастин", tr="cut"),
 k("позичає", "big", text="$10000", acc=["$"], size=240, count=[0, 10000, "$#"], cdur=1.2, sub="у борг у друзів і родичів"),
 k("невеликий", "photo", img="p13.jpg", tag="В'ЄТНАМСЬКИЙ РЕСТОРАН", tr="cut"),
 k("Справи", "video", vid="rain_1.mp4", text="СПРАВИ ЙДУТЬ ПОГАНО", acc=["ПОГАНО"], size=130, freeze="погано."),
 k("Зате", "video", vid="cook_1.mp4", text="ЛОКШИНА БЕЗ ВАРІННЯ", acc=["БЕЗ"], size=130),
 k("Залив", "video", vid="cup_1.mp4", kicker="окріп + 3 хвилини", punch=["готовий."], tr="cut"),
], [[0, "RetroFuture_Dirty_%28ISRC_USUAN1200041%29.mp3", 0, 1.0]])
