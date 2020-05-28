

#main file for project0
#Matt Huson
#CS5293

import argparse #to accept commandline args

def fetch_incidents(url) :
    '''
    takes a url and returns HTTP request object
    '''
    import urllib.request #to fetch pdf from url

    data = urllib.request.urlopen(url) #gets data from url as HTTP request object
    
    return data #return HTTP request object

def extract_incidents(data) :
    '''
    takes HTTP request object and returns an array
    of strings containing each line of the pdf described by
    the HTTP request object
    '''
    import PyPDF2 as p2 #to process pdf
    import tempfile #to store pdf data
    import re #to separate lines

    incidents = [] #array to hold incidents
    fp = tempfile.TemporaryFile() #create temporary file to hold pdf data
    fp.write(data.read()) #read data from HTTP request object and write to temp file
    fp.seek(0) #move cursor to beginning of file
    pdfReader = p2.pdf.PdfFileReader(fp) #read pdf data from HTTP request object
    numPages = pdfReader.getNumPages() #get number of pages from pdf
    
    content = "" #string to hold text from pdf
    for i in range(numPages): #iterate through pages
        content += pdfReader.getPage(i).extractText() #add text to content string
    content = content.replace('\nNORMAN POLICE DEPARTMENT\nDaily Incident Summary (Public)', '') #remove header
    index = [m.start() for m in re.finditer(r'\d+/\d+/\d+', content)] #use regex to find indices of beginning of each line of text
    
    for ind in range(len(index)): #iterate through line start indices
        if ind < len(index) - 1: #leave out "date retrieved line"
            incidents.append(content[index[ind]:(index[ind+1]-1)]) #separate out each line from the start index to the end index

    return incidents #return array of strings
    
    


def create_db(db) :
    '''
    takes db name and creates table called "incidents"
    returns nothing
    '''
    import sqlite3 as sq #for creating and accessing db
    conn = sq.connect(db) #create connection, or create local db if not already exists
    c = conn.cursor() #create cursor for db

    c.execute('DROP TABLE IF EXISTS incidents') #drop table so that incidents table will be empty when done
    c.execute('CREATE TABLE incidents(incident_time TEXT, incident_number TEXT, incident_location TEXT, nature TEXT, incident_ori TEXT)')
    #create incidents table

    conn.commit() #commit changes
    c.close() #close cursor
    conn.close() #close connection

    

def populate_db(db, incidents) :
    '''
    takes db name and incidents array of strings
    breaks strings down into constituent parts and inserts in db
    returns nothing
    '''
    import sqlite3 as sq #for accessing db
    import re #for breaking down strings
    conn = sq.connect(db) #create connection to db
    c = conn.cursor() #create cursor

    for line in incidents: #iterate through each string in array
        return_index = [m.start() for m in re.finditer(r'\n', line)] #find each line break in the string
        number_index = len(return_index) #get number of line breaks
        date_time = line[0:return_index[0]] #get text from beginning of string to first line break
        number = line[return_index[0]+1:return_index[1]] #get text from just after first linebreak to second linebreak
        location = line[return_index[1]+1:return_index[number_index-2]].replace('\n', '')
        '''get location text; in order to avoid errors due to multiple linebreaks, this reaches around from the end of the array to get
        the end index for the location portion, and removes any extra linebreaks'''

        nature = line[return_index[number_index-2]+1:return_index[number_index-1]] #get text from second to last linebreak to last linebreak
        ORI = line[return_index[number_index-1]+1:] #get text from last linebreak to end of string
        if location == '':#when "nature" is blank, above code gives an empty string for location and puts the address in the nature variable...
            location = nature #this if statement moves the address to the location and calls nature "undefined"
            nature = 'Not Entered'
        c.execute("INSERT INTO incidents VALUES (?,?,?,?,?)", (date_time, number, location, nature, ORI)) #insert data into db
 
    conn.commit() #commit changes
    c.close() #close cursor
    conn.close() #close connection

def status(db) :
    '''
    takes db name
    retrieves counts of each incident nature into a pandas dataframe
    prints each nature and associated count
    returns nothing
    '''
    import pandas as pd #to handle db output
    import sqlite3 as sq #to access db

    conn = sq.connect(db) #create db connection

    df = pd.read_sql_query("SELECT nature, COUNT(*) AS count FROM incidents GROUP BY nature", conn) #get nature info
    
    conn.close() #close connection
    

    for i in range(len(df.index)): #iterate through rows in dataframe
        print(df.iloc[i, 0], "|", df.iloc[i, 1], sep = '') #print each nature and its count

#url = "http://normanpd.normanok.gov/filebrowser_download/657/2020-02-24%20Daily%20Incident%20Summary.pdf"

def main(url):
    '''
    takes url
    creates incidents table
    prints each incident nature and count of occurence
    returns nothing
    '''
    data = fetch_incidents(url)

    incidents = extract_incidents(data)
    
    db = 'normanpd.db'

    create_db(db)

    populate_db(db, incidents)

    status(db)



if __name__ == '__main__':
    #main guard
    parser = argparse.ArgumentParser() #create argument parser object
    parser.add_argument("--incidents", type=str, required=True, #add passed commandline object
                         help="The incident summary url.")
     
    args = parser.parse_args() #parse argument and create argument object
    if args.incidents: #if argument object has an incidents argument
        main(args.incidents) #proceed with main using the passed url

