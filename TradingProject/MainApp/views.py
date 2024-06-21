# MainApp/views.py

from django.shortcuts import render
from .models import Candle
import pandas as pd
import json
import os
import asyncio

def home_page(request):
    return render(request,'base.html')

async def convert_to_timeframe(one_minute_candles, timeframe_minutes):
    aggregated_candles = []
    current_candle = None
    current_timeframe = None

    for candle in one_minute_candles:
        candle_datetime = candle.date
        if current_candle is None:
            current_candle = candle
            current_timeframe = candle_datetime
        elif (candle_datetime - current_timeframe).total_seconds() >= (timeframe_minutes * 60):
            aggregated_candles.append(current_candle)
            current_candle = candle
            current_timeframe = candle_datetime

    # Add last candle
    if current_candle:
        aggregated_candles.append(current_candle)

    return aggregated_candles

def upload_csv(request):

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        timeframe = int(request.POST.get('timeframe'))  # Get the timeframe 
        # Read CSV data using pandas
        df = pd.read_csv(csv_file)

        # Process the data
        candles = []
        for index, row in df.iterrows():
            candle = Candle(
                open=row['OPEN'],
                high=row['HIGH'],
                low=row['LOW'],
                close=row['CLOSE'],
                date=row['DATE'] + ' ' + row['TIME']
            )
            candles.append(candle)

        # Convert to desired timeframe (async operations)
        loop = asyncio.get_event_loop()
        converted_candles = loop.run_until_complete(convert_to_timeframe(candles, timeframe))

        # Serialize data to JSON
        json_data = []
        for candle in candles:
            json_data.append({
                'id': candle.id,
                'open': float(candle.open),
                'high': float(candle.high),
                'low': float(candle.low),
                'close': float(candle.close),
                'date': candle.date.strftime('%Y-%m-%d %H:%M:%S')  # Format date
            })

        # Save JSON data to a file
        json_file_path = os.path.join('media', 'converted_data.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file)

        return render(request, 'result.html', {'json_file_path': json_file_path})
    return render(request, 'result.html')
