import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.db.models import Count, Sum, Avg


def linechart(object_inst, request_obj, obj_name, total, timeframe=""):
    """
    Generate a line chart using Plotly based on the given queryset and request object.

    Args:
        timeframe:
        object_inst (QuerySet): The queryset of objects (transactions or incomes).
        request_obj (HttpRequest): The request object.
        obj_name (str): The name of the object (e.g., 'Transaction' or 'Income').

    Returns:
        str: HTML code for the generated line chart.
    """
    # Create a DataFrame from the queryset
    df = pd.DataFrame(dict(
        Date=[field.date.date() for field in object_inst],
        Amount=[object_inst.filter(date__date=field.date.date()).aggregate(sum=Sum('amount')).get('sum') for field in
                object_inst],
    ))

    # Sort the DataFrame by date in descending order
    df.sort_values(by='Date', ascending=False, inplace=True)

    # Create a Plotly figure
    fig = go.Figure(
        data=go.Scatter(
            x=df.get('Date'),
            y=df.get('Amount'),
            mode='lines+markers',
        )
    )

    # Update layout settings for the chart
    fig.update_layout(
        title={
            'text': f"{obj_name} Data - ({request_obj.session.get('user_currency')}{total}) {timeframe}",
            'font_size': 22,
            'xanchor': 'center',
            'x': 0.5
        },
        xaxis_title="Date",
        yaxis_title="Amount",
    )

    # Convert the figure to HTML code
    chart = fig.to_html()
    return chart


def barchart(object_inst, request_obj, obj_name, total, timeframe=""):
    # Create a DataFrame from the queryset
    df = pd.DataFrame(dict(
        Categories=[field for field in object_inst.keys()],
        SubTotal=[field for field in object_inst.values()],
    ))

    # Sort the DataFrame by date in descending order
    df.sort_values(by='Categories', ascending=False, inplace=True)

    fig = px.bar(df, y='SubTotal', x='Categories', text_auto='.2s',
                 title=f"{obj_name} and Sub-Total - ({request_obj.session.get('user_currency')}{total}) {timeframe}")
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

    chart = fig.to_html()
    return chart
