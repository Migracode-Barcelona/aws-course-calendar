import csv
from datetime import datetime, timedelta

# Function to parse date from the CSV file
def parse_date(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y %H:%M')

# Function to check if a given date is a weekend (Saturday or Sunday)
def is_weekend(date):
    return date.weekday() in [5, 6]

# Function to add a day to a given date, skipping weekends
def add_weekday(date, days):
    new_date = date + timedelta(days)
    while is_weekend(new_date):
        new_date += timedelta(1)
    return new_date

# Open the CSV file
with open('data.csv', 'r') as csvfile:
    # Create a CSV reader
    csvreader = csv.reader(csvfile)

    # Skip the header row
    next(csvreader)

    start_date = parse_date('15/01/2024 18:00')
    # Iterate through each row in the CSV file
    for row in csvreader:
        title = row[5]  # Assuming the title is in the 5 column
        duration = float(row[4])  # Assuming the duration is in the 4 column

        # Calculate the end date based on the duration
        end_date = start_date + timedelta(minutes=duration)

        # Check if the event ends before 21:30
        if end_date.time() < datetime.strptime('21:30', '%H:%M').time():
            event_end_date = end_date
        else:
            # Add it the following day at 18:00
            event_end_date = add_weekday(start_date, 1)
            event_end_date = event_end_date.replace(hour=18, minute=0)

        # Skip weekends
        while is_weekend(event_end_date):
            event_end_date = add_weekday(event_end_date, 1)
            


        print(f"Event: {title}, Start Date: {start_date}, End Date: {event_end_date}")
        start_date = end_date