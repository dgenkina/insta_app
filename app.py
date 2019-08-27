from flask import Flask, render_template, request

from wtforms import Form
from wtforms import fields, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import re
import get_data_and_plot
from get_data_and_plot import plot_sub_graph
app = Flask(__name__)



class InputHashtags(Form):
    tags = fields.StringField()

  #  site = QuerySelectField(query_factory=Site.query.all)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    set_data_params_form = InputHashtags()
    if request.method == 'GET':
        plot = None
        recommended = None
    elif request.method == 'POST':
        tags = str(request.form.get('tags'))
        tags = tags.replace('#','')        
        plot, recommended = plot_sub_graph(tags)
#        graph = plot_closing_prices(ticker_name=ticker,year=year,month=month)
    return render_template('tickers.html', form=set_data_params_form, recommended = recommended, plot=plot)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=33507)
