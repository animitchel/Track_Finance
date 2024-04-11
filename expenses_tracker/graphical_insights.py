import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.db.models import Count, Sum, Avg


def linechart(object_inst, request_obj, obj_name):
    df = pd.DataFrame(dict(
        Date=[field.date.date() for field in object_inst],
        Amount=[object_inst.filter(
            date__date=field.date.date()).aggregate(sum=Sum('amount')).get('sum') for field in object_inst],
    ))

    df.sort_values(by='Date', ascending=False, inplace=True)

    # df.plot(x='Date', y='Amount')
    # fig.update_traces(name= < VALUE >, selector = dict(type='scatter'))
    # fig = go.Figure()
    fig = go.Figure(
        data=go.Scatter(
            x=df.get('Date'),
            y=df.get('Amount'),
            mode='lines+markers',
        )
    )

    fig.update_layout(
        title={
            'text': f"{obj_name} Data ({request_obj.session.get('user_currency')})",
            'font_size': 22,
            'xanchor': 'center',
            'x': 0.5
        },
        xaxis_title="Date",
        yaxis_title="Amount",
    )

    # fig = px.line(
    #     df,
    #     x='Date',
    #     y='Amount',
    #     markers=True,
    #     title=f"Transaction Data ({request.session.get('user_currency')})"
    # )

    chart = fig.to_html()
    return chart
