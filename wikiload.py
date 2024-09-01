import json

wikifile = "tmp/res1/AA/wiki_01"


text = []
stop = 10000
with open(wikifile,"r") as f:
    for strjson in f:
        js = json.loads(strjson)
        """ Example of an entry 
        {"id": "2551096", "revid": "124082", "url": "https://fr.wikipedia.org/wiki?curid=2551096", "title": "Ice d'Indianapolis", "text": "L'Ice d'Indianapolis est une franch
ise de hockey sur glace ayant \u00e9volu\u00e9 dans la Ligue internationale de hockey et dans la Ligue centrale de hockey.\nHistorique.\nL'\u00e9quipe a \u00e9t\u00e9
 cr\u00e9\u00e9e en 1988 \u00e0 Indianapolis dans l'\u00c9tat de l'Indiana et \u00e9volua dans la LIH o\u00f9 ils furent le club-\u00e9cole des Blackhawks de Chicago 
durant quelques ann\u00e9es avant de passer ensuite en 1999 dans la LCH o\u00f9 ils rest\u00e8rent jusqu'en 2004. Le Ice remporte la Coupe Turner remis au vainqueur d
es s\u00e9ries \u00e9liminatoires dans la LIH en 1989-1990 sous l'entra\u00eeneur Darryl Sutter. Ils remportent \u00e9galement la Coupe Miron remis au champion des s\
u00e9ries dans la ligue centrale en 2000.\nSaisons en LIH.\n\"Note: PJ : parties jou\u00e9es, V : victoires, D : d\u00e9faites, N : matchs nuls, DP : d\u00e9faite en 
prolongation, DF : d\u00e9faite en fusillade, Pts : Points, BP : buts pour, BC : buts contre, Pun : minutes de p\u00e9nalit\u00e9\""}
        """

        # found a text entry
        if js and js.get("text"):
            # remove \n in text and replace \' with '
            text.append(js.get("text").replace("\n"," ").replace("\'","'"))

print(text)
print(len(text))

