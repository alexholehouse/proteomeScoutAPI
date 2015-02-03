# ProteomeScoutAPI
#
# ===============================================================================
# ABOUT
# ===============================================================================
# Version 1.3
# 
# February 2015 
#
# By Alex Holehouse, Washington University in St. Louis [Pappu Lab]
# Contact alex.holehouse@gmail.com or https://github.com/alexholehouse
#
#
#
# ===============================================================================
# OVERVIEW
# ===============================================================================
# ProteomeScoutAPI is a Python module which can be used to connect to and parse
# ProteomeScout flatfiles. 
#
# Specifically, the goal of this module is to allow anyone to interact with 
# ProteomeScout data without the need to
#
# 1) Repeatedly query the ProteomeScout sever
#
# 2) Have any knowledge of SQL, or use an SQL-Python ORM
#
# 3) Facilitate rapid exploration of the ProteomeScout dataset
#
# ===============================================================================
# Usage
# ===============================================================================
# The general approach to usage is as follows
#
# 0) Import the proteomeScoutAPI module
#  
# 1) Create the API object by loading a flat file. ProteomeScout flat files can 
#    be obtained from https://proteomescout.wustl.edu/compendia
#
#    PTM_API = ProteomeScoutAPI('<flat filename goes here>')
#
# 2) Query the API object using the functions. Available functions are
#
#    PTM_API.get_phosphosites(ID)
#    PTM_API.get_PTMs(ID)
#    PTM_API.get_mutations(ID)
#
#    For more information on these functions I suggest reading the rest of the
#    source code, or once you've loaded an API object type
#
#    help(PTM_API.get_mutations)
#
# 3) The PTM_APU.uniqueKeys is a list of the unique accession numbers to provide
#    an easy way to loop over all the unique entries. NOTE THAT IDS HAVE REDUNDANCY
#    which is deliberate (and makes interfacing easy) but cycling over all the IDs
#    in the API object would be incorrect and lead to double counting
#
# ===============================================================================
# EXAMPLES
# ===============================================================================
# from proteomeScoutAPI import ProteomeScoutAPI 
#
# 
# ID = "O46631"
#  
# PTM_API = ProteomeScoutAPI("proteomescout_mammalia_20140831.tsv")
#
# PTM_API.get_mutations(ID)
#
# PTM_API.get_PTMs(ID)
#
# # the following loop prints all the phosphosites in all the proteins
# for ID in PTM_API.uniqueKeys():
#    print PTM_API.get_phosphosites(ID)
#
# ===============================================================================


# Exception if file is bad
class BadProteomeScoutFile(Exception):
    pass


class ProteomeScoutAPI:


    def __init__(self,filename):
        """ 
        filename should be a ProteomeScout flatfile
        """        

        self.database={}
        self.uniqueKeys=[]

        # this will throw and exception if there's a problem with the file
        self.__checkFile(filename)
        
        self.__buildAPI(filename)

    def __checkFile(self, filename):
        """
        Internal function to check we (apparently) have a valid
        proteomeScout file
        """
        
        try:
            with open(filename, 'r') as f:
                first_line = f.readline()
                
            if not len(first_line.split("\t")) == 19:
                raise BadProteomeScoutFile("N/A")
            
                
        except:
            BadProteomeScoutFile("Invalid ProteomeScout flat file %s.\nFile is invalid or corrupted" % str(filename))
                
        

    def __buildAPI(self, datafile):

        # read in the file line by line
        with open(datafile) as f:
            content = f.readlines()
            

        
        # read the flatfile headers and parse
        # the contents
        headers_raw = content[0].split('\t')

        headers=[]
        for i in headers_raw:
            headers.append(i.strip())

        # remove the header line from the read in data
        content.pop(0)

        
        # for each line in the data
        for line in content:

            # split the record and get the canonical ID
            record = line.split('\t')
            IDlist_raw = record[1].split(";")
            IDlist = []
            for ID in IDlist_raw:
                IDlist.append(ID.strip())
                
            # add the first ID to the list of unique keys
            self.uniqueKeys.append(IDlist[0])

            # now construct the object dictionary. Note we
            # have hardcoded the number of header columns here
            # though if in future versions of the ProteomeScout
            # dataset more columns are added you coulded extend this
            # here
            OBJ={}
            for i in xrange(2,19):
                OBJ[headers[i]] = record[i]
        
            # assign the object to each ID - note this means that
            # there are many IDs point to the same object (which 
            # is desriable, given the many-to-one mapping of
            # accessions to records). It also avoids the need
            # to contrain yourself to a specific type of accession
            # when delaing with the ProteomeScoutAPI
            for ID in IDlist:
                self.database[ID] = OBJ

    def get_PTMs(self, ID):
        """
        Return all PTMs associated with the ID in question.

        POSTCONDITIONS:

        Returns a list of tuples of modifications
        [(position, residue, modification-type),...,]
        
        Returns -1 if unable to find the ID

        Returns [] (empty list) if no modifications        

        """
        
        try:
            record = self.database[ID]
        except KeyError:
            return -1

        mods = record["modifications"]
        
        mods_raw=mods.split(";")
        mods_clean =[]
        for i in mods_raw:
            tmp = i.strip()
            tmp = tmp.split("-")
            
            # append a tuple of (position, residue, type)
            mods_clean.append((tmp[0][1:], tmp[0][0], "-".join(tmp[1:])))
        return mods_clean


    def get_phosphosites(self,ID):
        """
        Return all phosphosites associated with the ID in question.

        POSTCONDITIONS:

        Returns a list of tuples of phosphosites
        [(position, residue, phosphosite-type),...,]
        
        Returns -1 if unable to find the ID

        Returns [] (empty list) if no modifications        

        """

        mods = self.get_PTMs(ID)
        
        if mods == -1:
            return -1
        
        phospho=[]
        for mod in mods:
            if mod[2].find("Phospho") >= 0:
                phospho.append(mod)

        return phospho

    def get_mutations(self, ID):
        
        """
        Return all mutations associated with the ID in question.
        
        POSTCONDITIONS:

        Returns a list of tuples of phosphosites
        [(original residue, position, new residue),...,]
        
        Returns -1 if unable to find the ID

        Returns [] (empty list) if no mutations        

        """
        
        try:
            record = self.database[ID]
        except KeyError:
            return -1

        mutations = record["mutations"]
        if len(mutations) == 0:
            return []
        
        mutations_raw=mutations.split(";")
        mutations_clean=[]

        for i in mutations_raw:
            tmp = i.strip()            
            # append a tuple of (position, residue, type)
            mutations_clean.append((tmp[1:-1], tmp[0], tmp[-1]))

        return mutations_clean


    
                


        
        
