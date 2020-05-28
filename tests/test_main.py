#testfile for project0


def test_fetchincidents():
    '''
    takes no args
    tests that fetch_incidents works with the test url to get a good http response
    '''
    from project0 import main #to get fetch_incidents
    url = "http://normanpd.normanok.gov/filebrowser_download/657/Public%20Records%20Archive/02_February%202020/2020-02-23%20Daily%20Incident%20Summary.pdf" #test url
    data = main.fetch_incidents(url) #retrieve HTTP request object
    assert data.getcode() == 200 #code 200 indicates a successful http response

def test_extractincidents():
    '''
    takes no args
    tests that extract_incidents returns an array of strings
    and that the strings start with a date and end with an ori code
    '''
    from project0 import main #to get extract_incidents
    import re #for using regexes to test strings

    url = "http://normanpd.normanok.gov/filebrowser_download/657/2020-02-24%20Daily%20Incident%20Summary.pdf" #test url

    incidents = main.extract_incidents(main.fetch_incidents(url)) #get HTTP request object and extract incidents
    start_regex = re.compile(r'^\d+/\d+/\d+') #regular expression to test that each incident starts with a date
    match_start = [start_regex.match(incident) for incident in incidents] #test of above regex
    end_regex = re.compile(r'14009$|14005$|EMSSTAT$|OK0140200$') #regex to test that each incident ends with a code
    match_end = [end_regex.match(incident) for incident in incidents] #test of above regex
    assert len(incidents) == len(match_start) and len(incidents) == len(match_end) #see if the number of arrays == number of correct arrays

def test_createdb():
    '''
    takes no args
    tests if createdb creates a table named 'incidents'
    '''
    from project0 import main #to get create_db
    import sqlite3 as sq #to access db

    db = 'normanpd.db' #db name
    main.create_db(db) #run create_db
    conn = sq.connect(db) #create connection
    c = conn.cursor() #create cursor

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents'") #query to find incidents table
    checkvar = c.fetchall() #get array of tuples

    c.execute("SELECT COUNT(*) FROM incidents") #query to see if incidents is empty
    numentries = c.fetchall()[0][0] #get number of rows returned from query

    c.close() #close cursor
    conn.close() #close connection

    assert len(checkvar[0]) == 1 and numentries == 0 #check if only one empty table is returned by the query

def test_populatedb():
    '''
    takes no args
    tests populate_db to see if correct number of rows are entered
    and tests to make sure intra-column linebreaks didn't affect db entry by checking values in last column
    '''

    from project0 import main #to get populatedb
    import sqlite3 as sq #to access db
    import re #to test db entries

    db = 'normanpd.db' #db name

    main.create_db(db) #clear out anything that might be in incidents table and start fresh

    conn = sq.connect(db) #create connection
    c = conn.cursor() #create cursor

    incidents = ['2/24/2020 0:04\n2020-00003064\n1932 E LINDSEY ST\nBreathing Problems\nEMSSTAT', 
                '2/24/2020 0:04\n2020-00002270\n1932 E LINDSEY ST\n14005', 
                '2/24/2020 0:08\n2020-00014232\n2146 W\n BROOKS ST\nOpen Door/Premises Check\nOK0140200', 
                '2/24/2020 0:17\n2020-00014233\nOAKWOOD DR / WYLIE RD\nTraffic Stop\nOK0140200', 
                '2/24/2020 0:23\n2020-00014234\n400 12TH\n AVE NE\nTraffic Stop\nOK0140200'] 
    #sample incidents, with line breaks added to address, and one blank added to nature

    main.populate_db(db, incidents) #run populatedb

    c.execute("SELECT COUNT(incident_time) FROM incidents") #get number of rows in db
    count_inci = c.fetchall()[0][0] #get actual integer describing number of rows

    c.execute("SELECT incident_ori FROM incidents") #get ori column from table
    origins = [item[0] for item in c.fetchall()] #get values in ori column

    c.execute("SELECT incident_location FROM incidents") #get location column from table
    loc_length = all([len(item[0]) for item in c.fetchall()]) #check to make sure location isn't blank to deal with blank nature


    c.close() #close cursor
    conn.close() #close connection

    end_regex = re.compile(r'14009$|14005$|EMSSTAT$|OK0140200$') #regex to test if ori column has valid values
    match_origin = [end_regex.match(origin) for origin in origins] #test of ori column values

    assert count_inci == len(match_origin) == 5 and loc_length == True 
    '''test to make sure 5 rows were entered and those 5 rows had valid values, and that location length
    is >0 for all locations, making sure blank natures were handled properly'''



from unittest.mock import patch #import to mock print function
@patch('builtins.print') #mock the print function
def test_status(mock_print):
    '''
    takes mock_print as an argument
    tests final line of the status() print statement to ensure correctness
    '''
    
    from project0 import main #to get db functions
    
    db = 'normanpd.db' #db name
    
    main.create_db(db) #clear out anything that might be in incidents table and start fresh

    incidents = ['2/24/2020 0:04\n2020-00003064\n1932 E LINDSEY ST\nBreathing Problems\nEMSSTAT', 
                '2/24/2020 0:04\n2020-00002270\n1932 E LINDSEY ST\n14005', 
                '2/24/2020 0:08\n2020-00014232\n2146 W\n BROOKS ST\nOpen Door/Premises Check\nOK0140200', 
                '2/24/2020 0:17\n2020-00014233\nOAKWOOD DR / WYLIE RD\nTraffic Stop\nOK0140200', 
                '2/24/2020 0:23\n2020-00014234\n400 12TH\n AVE NE\nTraffic Stop\nOK0140200'] 
    #sample incidents, with line breaks added to address, and one blank added to nature
   
    main.populate_db(db, incidents) #run populatedb

    
    main.status(db) #run status(db), which runs a print command to test
    mock_print.assert_called_with('Traffic Stop', '|', 2, sep='') #test that the correct final line was printed


