from mk import mk, B
m = B("mivina")
mk("c2", "mivina", [
 m("У", "chapter", no="СПРАВА №2", text="НАРОДЖЕННЯ МІВІНИ"),
 m("Техноком.", "big", text="ТЕХНОКОМ", acc=["ТЕХНОКОМ"], size=220, sub="Харків, 1993"),
 m("кредит", "video", vid="loan_2.mp4", text="КРЕДИТ ПІД ВИСОКІ ВІДСОТКИ", acc=["ВИСОКІ"], size=110, tr="cut"),
 m("Ризик", "video", vid="coins_1.mp4", kicker="якщо не вийде, борг з'їсть усе"),
 m("дев'яносто", "polaroid", img="p24.png", w=900, h=330, rot=3, cap="Харків, 1995", stamp="1995"),
 m("Звідки", "big", text="MÌ VIỆT NAM", acc=["VIỆT"], size=200, sub="«в'єтнамська локшина», за однією з версій"),
 m("Мівіна", "list", title="ЧОМУ МІВІНА", acc=["МІВІНА"], items=[["01", "дешева"], ["02", "у кожному кіоску"], ["03", "не треба плити"], ["04", "не треба посуду"]], gap=1.9),
 m("Для", "video", vid="money_1.mp4", text="ІДЕАЛЬНА ЇЖА", acc=["ІДЕАЛЬНА"], size=160, tr="cut"),
 m("За", "big", text="$1000000", acc=["$"], size=220, count=[0, 1000000, "$#"], cdur=1.3, sub="продажі за два роки"),
 m("Студенти", "photo", img="p05.jpg", kicker="гуртожитки", tr="cut"),
 m("робітники", "video", vid="bus_3.mp4", kicker="на зміну", tr="cut"),
 m("школярі", "video", vid="ramen_1.mp4", text="СУХОЮ, ЯК ЧІПСИ", acc=["ЧІПСИ"], size=140, tr="cut"),
 m("Подейкують,", "video", vid="ramen_2.mp4", kicker="смачніше, ніж за інструкцією", freeze="інструкцією."),
], [[0, "Funkorama_%28MacLeod%2C_Kevin%29_%28ISRC_USUAN1100474%29.oga", 0, 1.0]])
