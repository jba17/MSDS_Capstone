import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import seaborn as sns
import matplotlib.patches
import scipy.stats as stats
from datetime import datetime
plt.style.use('ggplot')

def objectivePercent(df, ax=None, title=None):
    #assigning ax variable if not given for plotting
    if ax is None:
        ax = plt.gca()
        
    #calculate percentages of scores with/without objectivity (neutral value =/!= 1)
    objective = pd.crosstab(df['date'].astype(str), df['neu'] == 1)
    objective_rate = objective.div(objective.sum(1).astype(float), axis=0)
    
    #plot objective_rate percentages in a stacked bar graph
    objective_rate.plot(kind='barh', ax=ax, stacked=True, color=['blue','gray'])
    
    #objective bar plot formatting
    ax.legend(['Objective', 'Neutral'], loc=1)
    ax.set_xlabel('Percentage', color='k')
    ax.set_ylabel('Date', color='k')
    ax.tick_params('both', colors='k')
    ax.set_title(title)
    ax.invert_yaxis()
    plt.tight_layout()
    
def objectiveDistribution(df_obj, df_polar, ax=None, title=None):   
    #assigning ax variable if not given for plotting
    if ax is None:
        ax = plt.gca()
        
    #generate distribution plot for each set of values following a beta distribution
    sns.distplot(df_polar['value'].abs(), ax=ax, fit_kws={'color':'blue'}, fit=stats.beta, hist=None, kde=False)
    sns.distplot(df_obj['neu'], ax=ax, fit_kws={'color':'gray'}, fit=stats.beta, hist=None, kde=False)
    
    #get plotted lines for shading
    l1 = ax.lines[0]
    l2 = ax.lines[1]

    #get xy coordinate data from each plotted line for shading
    x1 = l1.get_xydata()[:,0]
    y1 = l1.get_xydata()[:,1]
    x2 = l2.get_xydata()[:,0]
    y2 = l2.get_xydata()[:,1]
    
    #shade between the two sets of xy coordinate data from each plotted line
    ax.fill_between(x1,y1, color="blue", alpha=0.3)
    ax.fill_between(x2,y2, color="gray", alpha=0.3)

    #objective distribution plot formatting
    ax.legend(['Objective', 'Neutral'], loc=1)
    ax.set_xlabel('Percentage', color='k')
    ax.tick_params('both', colors='k')
    ax.yaxis.set_visible(False)
    ax.set_title(title)
    plt.tight_layout()    

def dailyPriceSentimentChart(df, file_suffix):
    #initialize figure with title
    fig, ax1 = plt.subplots()
    plt.title(file_suffix)
    
    #plot price_diff series against date
    ax1.plot(df.date, df.price_diff, 'b.:', markersize=20, markerfacecolor="None")

    #determine maximum distance away from zero as factor of 100 (for y axis labels)
    max_diff = np.ceil(max(np.abs(ax1.get_ybound()))/100)*100
    
    #get the properly spaced xlabels determined by seaborn
    xlabels = ax1.get_xticklabels()

    #price_diff series plot formatting
    ax1.set_xlabel('Date', color = 'k')
    ax1.tick_params('x',labelrotation=-45)
    ax1.set_xticklabels(xlabels, ha="left")
    ax1.tick_params('x', colors='k')
    ax1.set_ylabel('Price Change (USD)', color='b')
    ax1.tick_params('y', colors='b')
    ax1.yaxis.set_ticks(np.linspace(-max_diff,max_diff,5))

    #new plot with matching x axis as price_diff
    ax2 = ax1.twinx()

    #plot horizontal line to show +/- boundary
    horiz_line = np.array([0 for i in range(len(df.date))])
    ax2.plot(df.date,horiz_line, 'k')

    #plot daily_sentiment series against date
    ax2.plot(df.date, df.value, 'ms:', markersize=10, markerfacecolor="None")

    #determine maximum distance away from zero as factor of 10 (for y axis labels)
    max_pol = np.ceil(max(np.abs(ax2.get_ybound()))*10)/10

    #daily_sentiment series plot formatting
    ax2.set_ylabel('Average Polarity', color='m')
    ax2.tick_params('y', colors='m')
    ax2.yaxis.set_ticks(np.linspace(-max_pol,max_pol,5))

    #custom legend for both plots
    blue_circle = mlines.Line2D([],[], color='b', marker='.', markersize=10, markerfacecolor="None", label='Price', linestyle=":")
    pink_square = mlines.Line2D([],[], color='m', marker='s', markersize=5, markerfacecolor="None", label='Polarity', linestyle=":")
    plt.legend(handles=[blue_circle,pink_square], loc = "lower right")

    #saving and showing plots
    path = 'figures/PriceSentimentChart_' + file_suffix + '.png'
    plt.savefig(path, bbox_inches='tight')
    plt.show()
    
    

def dailySentimentsOverview(df, file_suffix):

    #converting all negative polarity values to positive numbers for plotting
    df.value = abs(df.value)

    #create figure with subplots that share a x axis and properly sized to one another
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8,6), gridspec_kw={'height_ratios':[3,1]})

    #custom colors for +/- values
    colors = ['green', 'red']

    #plot first subplot, boxplots for +/- polarity values by day
    sns.boxplot(data=df, x='date', y='value', palette=colors, hue='variable', ax=ax1)
    
    #polarity boxplot formatting
    ax1.set_title(file_suffix)
    ax1.set_ylabel('Polarity', color = 'k')
    ax1.tick_params('y', colors='k')
    ax1.xaxis.set_visible(False)
    ax1.legend_.set_title(None)

    #looping through all boxplot chart elements to remove color inside boxplot boxes and change all
    #line and marker elements to proper color according to +/- polarity group
    for i,artist in enumerate(ax1.artists):
        col = artist.get_facecolor()
        artist.set_edgecolor(col)
        artist.set_facecolor('None')
    
        for j in range(i*6,i*6+6):
            line = ax1.lines[j]
            line.set_color(col)
            line.set_mfc(col)
            line.set_mec(col)

    #plot second subplot, bar chart showing number of +/- polarity values by day
    df.date = df.date.astype(str) #convert date objects to strings
    sns.countplot(data=df, x='date', palette=colors, hue='variable', linewidth=2, ax=ax2)
    
    #get the properly spaced xlabels determined by seaborn
    xlabels = ax2.get_xticklabels()

    #polarity bar chart formatting
    ax2.set_xlabel('Date', color = 'k')
    ax2.tick_params('x',labelrotation=-45)
    ax2.set_xticklabels(xlabels, ha="left")
    ax2.tick_params('both', colors='k')
    ax2.set_ylabel('Count', color = 'k')
    ax2.legend_.remove()

    #looping through all bar chart elements to remove color inside bars and change its edges to
    #proper color according to +/- polarity values
    back_col = ax2.get_facecolor() #chart background color
    for child in ax2.get_children():
        if isinstance(child, matplotlib.patches.Rectangle):
            col = child.get_facecolor()
            if not col == back_col: #checking to make sure Rectangle is bar and not axes Rectangles
                child.set_edgecolor(col)
                child.set_facecolor('None')

    #tighten subplot spacing
    plt.subplots_adjust(hspace=.03)
    
    #saving and showing plots
    path = 'figures/SentimentsOverviewChart_' + file_suffix + '.png'
    plt.savefig(path, bbox_inches='tight')
    plt.show()