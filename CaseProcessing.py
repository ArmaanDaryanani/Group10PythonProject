"""
* Project 10, ENGR1110
* GUI File
* Last Updated 11/14/23
"""


from datetime import datetime, timedelta

class CaseProcessing:
    def __init__(self, filename):
        self.filename = filename

    def get_list(self):
        with open(self.filename, 'r') as file, open('processed_total_deaths.txt', 'w') as output_file:
            num_lines = 0
            num_days = 0
            output_dict = {}  #use dictionary instead of list

            for line in file:
                # throw away first line
                if num_lines == 0:
                    num_lines += 1
                    continue
                else:
                    num_days += 1
                    num_lines += 1

                    # repeatedly replace consecutive commas with ",0,"
                    while ',,' in line:
                        line = line.replace(',,', ',0,')

                    death_list = line.strip().split(",")  # strip removes any leading or trailing whitespace
                    date = death_list[0]  #extract date from the list
                    deaths = [int(float(val)) if val else 0 for val in
                              death_list[1:]]  #convert the rest into a list of integers (with 0 for empty strings)

                    output_dict[date] = deaths  #add to dictionary

                    output_file.write(','.join(death_list) + '\n')  # write processed data to the new file

            return output_dict

    def total_days_passed(start_date, end_date):
        #YYYY-MM-DD
        date1 = datetime.strptime(start_date, '%Y-%m-%d').date()
        date2 = datetime.strptime(end_date, '%Y-%m-%d').date()

        delta = date2 - date1
        return delta.days

    def get_country_deaths_list_per_date(self, day, month, year):
        output_dict = self.get_list()
        date_str = "{:04d}-{:02d}-{:02d}".format(int(year), int(month), int(day))
        return output_dict[date_str]

    def exclude_indexes(self, dict, list_needed=False):
        excluded_list = ["World", "Africa", "Asia", "Europe", "European Union", "Low income",
                         "Lower middle income", "North America", "Saint Martin (French part)",
                         "South America", "Upper middle income"]

        for val in excluded_list:
            dict.pop(val, None)

        if list_needed:
            return list(dict.values())
        else:
            return dict

    def get_all_countries(self):
        with open(self.filename, 'r') as file:
            first_line = file.readline().split(',')
            first_line.remove("date")
            first_line[-1] = "Zimbabwe"
        return first_line

    def get_country_deaths_dict(self, day, month, year):
        deaths_list = self.get_country_deaths_list_per_date(day, month, year)
        country_list = self.get_all_countries()

        country_deaths_dict = dict(zip(country_list, deaths_list))
        return country_deaths_dict




if __name__ == "__main__":
    data = CaseProcessing("total_deaths.txt")
    data.construct_data("total_deaths.txt")
