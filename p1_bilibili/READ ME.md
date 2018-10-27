### For practice
### All spiders should work and deliver the same result

#### Updates:
- 3/29/2017: fixed ConnectionError problem, revised code to get timestamp from spider1, which shortens time by half!
- 3/28/2017: bilibili\_get\_video\_info.py completed;
- 3/15/2017: uploaded sample output csv file; added a solution of opening output files to Mac users  
- 3/14/2017: \_clean completed; planning on "run_all.py"
- 3/13/2017: \_explore completed; working on \_clean

#### Structure:
- spiders:
	- spider\_bilibili\_explore.ipynb: initial spider to explore and practice. all errors were saved as a reminder.
	- spider\_libilili\_clean.ipynb: organized file. I try to put everything into functions.
	- bilibili\_get\_video\_info.py: automated .py file. Two ways to collect info: input mids or automate with a pre-defined list. Switch between them by commenting and uncommenting.
	- Retrieve All.ipynb: notebook version of bilibili\_get\_video\_info
- sample\_image.png: what the output csv file should look like.
- sample\_stat\_43536\_2017-03-28\_22'32'07.csv: sample output csv file.
- info retrieved\_by date: inside the folder are folders named by retrieving dates.

#### This spider aims to find all important statistics about all videos of a given user: 
- input: user's mid
- output: a csv file that contains the following information:
	- aid
	- title
	- url
	- date
	- time
	- length
	- play
	- danmaku (a number)
	- review
	- favorites
	- coin

#### Output file:
['sample_stat_43536_2017-03-28_22'32'07.csv'](https://github.com/estepona/Python_Spiders/blob/master/1%20bilibili/sample_stat_43536_2017-03-28_22'32'07.csv) is a sample output file.

#### Issues:
- A ConnectionError occurred with too many data to retrieve.
