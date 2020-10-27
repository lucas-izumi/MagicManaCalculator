from mtgtools.MtgDB import MtgDB


class MtgDatabase:
    mtg_db = MtgDB('my_db.fs')
    cards = mtg_db.root.mtgio_cards
    total_cmc = 0
    mana_colors = {'G': 0, 'R': 0, 'U': 0, 'B': 0, 'W': 0, 'C': 0}

    def update_db(self):
        self.mtg_db.mtgio_update()()

    def get_card(self, card_name):
        return self.cards.where_exactly(name=card_name)

    def add_cmc(self, cmc):
        self.total_cmc += cmc

    def add_colors(self, color_list):
        for character in color_list:
            try:
                self.mana_colors[character] += 1
            except KeyError:
                try:
                    colorless = int(character)
                    self.mana_colors['C'] += colorless
                except ValueError:
                    continue


m = MtgDatabase()
# m.update_db()

lista = m.get_card('Glowstone Recluse')
print(type(lista))
print(lista[0].name)
print(lista[0].cmc)
m.add_cmc(lista[0].cmc)
print(lista[0].mana_cost)
print(m.mana_colors)
m.add_colors(lista[0].mana_cost)
print(m.mana_colors)

# lista = m.get_card('Golgothian Sylex')
# print(type(lista))
# print(lista[0])
# lista = m.get_card('Golgothian Sylexade')
# print(type(lista))
# print(lista)
