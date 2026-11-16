from mk import mk, B
b, h, m = B("hook"), B("hook"), B("mivina")
mk("c0", "hook", [
 h("Пачка", "big", text="ПАЧКА ЗА КОПІЙКИ", acc=["КОПІЙКИ"], size=210, sub="Харків, 1995"),
 b("студенти", "video", vid="student_1.mp4", kicker="студенти в гуртожитках", tr="cut"),
 m("школярі", "photo", img="p06.jpg", tag="СУХОЮ, З ПАКЕТА", punch=["сухою,"], tr="cut"),
 b("людина,", "big", text="$34 МЛРД", acc=["МЛРД"], size=220, count=[0, 34, "$#"], cdur=1.4, sub="статок творця, за оцінкою Forbes"),
 b("власний", "photo", img="p22.jpg", tag="VINFAST", tr="cut"),
 b("курорти", "photo", img="p26.jpg", tag="VINPEARL", tr="cut"),
 b("почалося", "photo", img="p02.jpg", tag="ХАРКІВ", punch=["Харкові."]),
 h("Привіт,", "big", text="ATTIC FILES", acc=["FILES"], size=230, sub="речі, з якими ми виросли", tr="flash"),
 m("Сьогодні", "polaroid", img="p24.png", w=900, h=330, rot=-3, cap="жовта пачка, яку знає кожен", pos="center"),
 m("Розберемося,", "list", title="ПИТАННЯ", acc=["ПИТАННЯ"], items=[["01", "хто її вигадав"], ["02", "чому вона стала словом"], ["03", "що з нею сталося у війну"]], gap=1.25),
], [[0, "Super_Power_Cool_Dude_%28ISRC_USUAN1600036%29.mp3", 0, 1.0], [7, "Digital_Lemonade_%28ISRC_USUAN1700010%29.mp3", 0, 1.0]], hook=True)
