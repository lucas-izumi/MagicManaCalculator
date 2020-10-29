from mtgtools.MtgDB import MtgDB
import math


ERR_BUSY = "Search process is currently busy. Try again later!"
ERR_BAD_FORMAT = "List format incorrect!"
ERR_NO_ERROR = "List successfully parsed!"

GLOBALMODIFIER = 0.92  # the modifier for tweaking the final outcomes
CARDCOUNTREF = 36  # the baseline number of cards to base the algorithm on
MANACOUNTREF = 24  # the baseline number of mana cards
MANACOSTPERCARDREF = 3  # the baseline mana cost per card average


class MtgDatabase:
    total_cmc = 0
    max_cards = 0
    total_cards = 0
    mana_colors = {'G': 0, 'R': 0, 'U': 0, 'B': 0, 'W': 0, 'C': 0, 'Generic': 0}
    suggested_mana_colors = {'G': 0, 'R': 0, 'U': 0, 'B': 0, 'W': 0, 'C': 0, 'Generic': 0}
    total_coloured_mana_cost = 0

    average_mana_per_card = 0
    card_count_modifier = 0
    mana_cost_modifier = 0
    suggested_total_mana = 0

    def update_db(self, mtg_db):
        mtg_db.mtgio_update()

    def get_card(self, cards, card_name):
        return cards.where_exactly(name=card_name)

    def add_cmc(self, cmc, qtd):
        self.total_cmc += (cmc * qtd)

    def add_colors(self, color_list, qtd):
        for character in color_list:
            try:
                self.mana_colors[character] += qtd
                self.total_coloured_mana_cost += qtd
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

    def load_stats(self, f):
        try:
            mtg_db = MtgDB('my_db.fs')
        except:
            return ERR_BUSY
        cards = mtg_db.root.mtgio_cards
        for lines in f.splitlines():
            try:
                if lines[0] == '/' or lines[0] == '' or lines[0] == '\n':
                    continue
                else:
                    try:
                        int(lines[0])
                    except ValueError:
                        return ERR_BAD_FORMAT
            except IndexError:
                continue
            try:
                s = self.parse_element(lines)
                pc = self.get_card(cards, s[1])
            except IndexError or UnboundLocalError:
                mtg_db.close()
                return ERR_BAD_FORMAT
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
                mtg_db.close()
                return "Card " + s[1] + " not found!"
        mtg_db.close()
        self.calculate_mana()
        return ERR_NO_ERROR

    def print_stats_str(self):
        results_str = "Mana Breakdown: " + str(self.mana_colors) + "<br>" + \
                        "Total converted mana cost: " + str(self.total_cmc) + "<br>" + \
                      "Total coloured mana cost: " + str(self.total_coloured_mana_cost) + "<br>" + \
                      "Total cards parsed: " + str(self.total_cards) + "<br>" + \
                        "Average Mana cost per Card: " + str(self.average_mana_per_card) + "<br>" + \
                      "Suggested Total Mana: " + str(self.suggested_total_mana) + "<br>" + \
                        "Suggested Mana: " + str(self.suggested_mana_colors)
        self.reset_values()
        return results_str

    def reset_values(self):
        self.total_cmc = 0
        self.total_cards = 0
        self.mana_colors = {'G': 0, 'R': 0, 'U': 0, 'B': 0, 'W': 0, 'C': 0, 'Generic': 0}
        self.suggested_mana_colors = {'G': 0, 'R': 0, 'U': 0, 'B': 0, 'W': 0, 'C': 0, 'Generic': 0}
        self.average_mana_per_card = 0
        self.card_count_modifier = 0
        self.mana_cost_modifier = 0
        self.suggested_total_mana = 0
        self.total_coloured_mana_cost = 0

    def calculate_mana(self):
        if self.total_cmc and self.total_cards:
            self.average_mana_per_card = self.total_cmc / self.total_cards
        else:
            self.average_mana_per_card = 0
        self.card_count_modifier = self.total_cards / CARDCOUNTREF
        self.mana_cost_modifier = self.average_mana_per_card / MANACOSTPERCARDREF
        self.suggested_total_mana = int(round(MANACOUNTREF * self.card_count_modifier * self.mana_cost_modifier *
                                              GLOBALMODIFIER))
        self.split_mana()

    def split_mana(self):
        for key in self.mana_colors:
            if key == 'Generic':
                continue
            mana = self.mana_colors[key]
            mana_total = mana / self.total_coloured_mana_cost * self.suggested_total_mana
            self.suggested_mana_colors[key] = int(round(mana_total))
