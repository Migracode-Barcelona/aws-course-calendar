import csv
from datetime import datetime, timedelta
from ics import Calendar, Event

# Function to parse date from the CSV file
def parse_date(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y %H:%M')

# Function to check if a given date is a skipped day (Friday, Sunday or Holidays)
def is_skipday(date):
    # Check if it's a Friday or Sunday
    if date.weekday() in [4, 6]:
        return True
    # Check if it's a holiday
    holidays = [
        '01/01/2024', '06/01/2024', '29/03/2024', '01/04/2024', '01/05/2024',
        '20/05/2024', '24/06/2024', '15/08/2024', '11/09/2024', '24/09/2024',
        '12/11/2024', '01/11/2024', '06/12/2024', '25/12/2024', '26/12/2024',
        '30/03/2024', '18/05/2024', '22/06/2024'
    ]
    return date.strftime('%d/%m/%Y') in holidays

def is_saturday(date):
    return date.weekday() == 5  # Saturday

# Function to add a day to a given date, skipping skipdays
def add_weekday(date, days):
    new_date = date + timedelta(days)
    while is_skipday(new_date):
        new_date += timedelta(1)
    return new_date

def is_valid_row(row): # invalid rows are lunches, breaks and flex times
    return not any(row[key] == 'TRUE' for key in ['is_break', 'is_lunch', 'is_flex_time'])

# Open the CSV file
with open('data.csv', 'r') as csvfile:
    # Create a CSV reader
    csvreader = csv.DictReader(csvfile)

    # Skip the header row
    next(csvreader)

    # Create an iCalendar
    cal = Calendar()

    # Initial start date
    start_date = parse_date('15/01/2024 18:00')
    start_hour = [18, 0]
    end_hour = '21:30'

    # flextime research 
    total_flex_time_before = []
    total_flex_time_after = []
    total_workdays = 0

    # Iterate through each row in the CSV file
    for row in csvreader:
        # flextime research 
        if (row['title'] == 'Flex Time'):
            total_flex_time_before.append(float(row['duration']))

        if is_valid_row(row):
            title = row['week_title']+" - "+row['title'] 
            duration = float(row['duration'])

            # Create a new event
            event = Event()
            event.name = title
            event.begin = start_date
            event.end = start_date + timedelta(minutes=duration)

            print("starts "+str(event.begin)+", ends "+str(event.end))

            # Check if the event ends before the end of the day
            if event.end.time() < datetime.strptime(end_hour, '%H:%M').time():
                # Create the event
                cal.events.add(event)
            else:
                # If there is time left at the end of the day, add flex time
                if start_date.time() < datetime.strptime(end_hour, '%H:%M').time():
                        flex_event = Event(name="Flex time", begin=start_date, 
                            end=start_date.combine(start_date.date(), datetime.strptime(end_hour, '%H:%M').time()))
                        cal.events.add(flex_event)

                        # flextime research 
                        total_flex_time_after.append((flex_event.end - flex_event.begin).total_seconds() / 60)
                        if ((flex_event.end - flex_event.begin).total_seconds() / 60 > 90):
                            print("BATARD "+str(flex_event))

                # Skip to the next working day
                start_date = add_weekday(start_date, 1)
                total_workdays += 1
                # Set the start and end hour depending on the day
                if is_saturday(start_date):
                    start_hour = [10, 30]
                    end_hour = '14:00'
                else:
                    start_hour = [18, 0]
                    end_hour = '21:30'

                # Set the hour for current day
                start_date = start_date.replace(hour=start_hour[0], minute=start_hour[1])

                # Update the event with the new start and end dates
                event.end = start_date + timedelta(minutes=duration)
                event.begin = start_date

                # Create the event
                cal.events.add(event)

            # Update start date for the next iteration
            start_date = event.end
    print(f'Total flex time original AWS (min): {sum(total_flex_time_before)}, Average: {sum(total_flex_time_before) / len(total_flex_time_before)}, Maximum: {max(total_flex_time_before)}, Minimum: {min(total_flex_time_before)} (over {12*5} working days)')
    print(f'Total flex time new schedule (min): {sum(total_flex_time_after)}, Average: {sum(total_flex_time_after) / len(total_flex_time_after)}, Maximum: {max(total_flex_time_after)}, Minimum: {min(total_flex_time_after)} (over {total_workdays} working days)')

# Write the iCalendar to a file
with open('output.ics', 'w') as ics_file:
    ics_file.writelines(cal)
