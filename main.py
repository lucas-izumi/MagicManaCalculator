from mtgtools.MtgDB import MtgDB


class MtgDatabase:
    mtg_db = MtgDB('my_db.fs')
    cards = mtg_db.root.mtgio_cards
    total_cmc = 0
    max_cards = 0
    total_cards = 0
    mana_colors = {'G': 0, 'R': 0, 'U': 0, 'B': 0, 'W': 0, 'C': 0, 'Generic': 0}

    def update_db(self):
        self.mtg_db.mtgio_update()()

    def get_card(self, card_name):
        return self.cards.where_exactly(name=card_name)

    def add_cmc(self, cmc, qtd):
        self.total_cmc += (cmc * qtd)

    def add_colors(self, color_list, qtd):
        for character in color_list:
            try:
                self.mana_colors[character] += qtd
            except KeyError:
                try:
                    generic_mana = (int(character) * qtd)
                    self.mana_colors['Generic'] += generic_mana
                except ValueError:
                    continue

    def parse_element(self, element):
        card_name = ''
        for elem in element.split():
            try:
                qtd = int(elem)
            except ValueError:
                card_name = card_name + elem + " "
        card_name = card_name.strip()
        return qtd, card_name

    def load_stats(self, input_file):
        f = open(input_file, "r")
        for lines in f:
            try:
                s = self.parse_element(lines)
                pc = self.get_card(s[1])
            except IndexError:
                return "List format incorrect!"
            try:
                if pc[0].type.find('Land') == -1:
                    self.total_cards += s[0]
                    print(pc[0].name)
                    try:
                        self.add_cmc(pc[0].cmc, s[0])
                        self.add_colors(pc[0].mana_cost, s[0])
                    except TypeError:
                        print("No CMC or Mana Cost for this card")
            except IndexError:
                return "Card " + s[1] + " not found!"
        return "List successfully parsed!"



m = MtgDatabase()
# m.update_db()
print(m.load_stats("deck.txt"))
print("Mana Breakdown: ", m.mana_colors)
print("Total converted mana cost: ", m.total_cmc)
print("Total cards parsed: ", m.total_cards)


# lista = m.get_card('Kozilek, the Great Distortion')
# print(type(lista))
# print(lista[0].name)
# print(lista[0].cmc)
# m.add_cmc(lista[0].cmc)
# print(lista[0].mana_cost)
# print(m.mana_colors)
# m.add_colors(lista[0].mana_cost)
# print(m.mana_colors)

# lista = m.get_card('Golgothian Sylex')
# print(type(lista))
# print(lista[0])
# lista = m.get_card('Golgothian Sylexade')
# print(type(lista))
# print(lista)
