from mk import mk, B
m, h = B("mivina"), B("hook")
mk("c7", "mivina", [
 m("Отже,", "photo", img="p10.jpg", tag="ПАЧКА ЗА КОПІЙКИ"),
 m("нагодувала", "video", vid="oldtv_1.mp4", text="НАГОДУВАЛА КРАЇНУ", acc=["КРАЇНУ"], size=150, tr="cut"),
 m("принесла", "video", vid="exchange_2.mp4", text="МІЛЬЙОНИ → МІЛЬЯРДИ", acc=["МІЛЬЯРДИ"], size=140),
 m("тепер", "video", vid="truck_1.mp4", kicker="Волинь → Європа", tr="cut"),
 m("Наступного", "photo", img="p04.jpg", kicker="можливо, найприбутковіший обід в історії України"),
 m("яка", "list", title="ВАША УЛЮБЛЕНА?", acc=["УЛЮБЛЕНА?"], items=[["01", "з куркою"], ["02", "з яловичиною"], ["03", "суха, просто з пакета"]], gap=1.0),
 h("Підписуйтеся", "big", text="ATTIC FILES", acc=["FILES"], size=230, sub="далі на горищі ще багато речей з дитинства", tr="flash"),
], [[0, "Audionautix-com-ccby-feelgoodfeel.mp3", 0, 1.0]], tail=1.5)
