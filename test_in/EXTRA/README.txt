The files in this folder are designed to fail when ran through the scripts.  They are incorrectly 
formatted or missing parameters needed in the simulation.

Running these files through the simulation will give a AssertionError describing the issue.




HOW TO RUN:

Move file(s) up one directory to "\test_in" or whatever the folder was renamed to.

Example: \test_in\EXTRA\testfail1.csv  ------> \test_in\testfail1.csv




Problems in each file:

	testfail1.csv - dist_to_alt_lookup and it's value has been shifted down multiple cells so 
			that there is now a gap in data.  All params must be in the first row along
			with it's corresponding value in the following row

	testfail2.csv - rider_mass and bike_mass have two values instead of only one. Each param
			can only hold 1 value. Make a new .csv with the 2nd value replacing the 1st
			to test how different params affect the simulation

	testfail3.csv - total_time is missing from the file. Make sure all the params are accounted for


	testfail4.csv - This file will not cause any issues with the output.  However there is an extra
			param and value associated with it in the file.  It is simply ignored.