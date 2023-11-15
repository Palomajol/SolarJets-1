import json
import datetime
import numpy as np

class MetaFile:
    '''
        Data class to read out the meta data for each of the subjects given in Zooniverse
    '''

    def __init__(self, file_name: str):
        '''
            Inputs
            ------
            file_name : meta data json file 
                Contains for each subject a set of meta data 
                keys {'#file_name_0','#file_name_14', '#sol_standard', '#width','#height',
                     '#naxis1', '#naxis2', '#cunit1', '#cunit2','#crval1','#crval2', '#cdelt1', '#cdelt2', 
                     '#crpix1', '#crpix2', '#crota2', '#im_ll_x', '#im_ll_y','#im_ur_x', '#im_ur_y'}
        '''
        try:
            data = json.load(open(file_name))
        except FileNotFoundError:
            print(f'{file_name} was not found')
            return
        except:
            print('This file could not be read out as a json, please check the format')
            return

        self.file_name = file_name
        self.data = data
        self.subjects = np.asarray([x['subjectId'] for x in data])
        self.SOL_unique = np.unique([x['data']['#sol_standard'] for x in data])

    def get_subjectid_by_solstandard(self, sol_standard: str):
        '''
        Get an array of subject id in the sol_standard HEK event
            Inputs
            ------
            sol_standard : str
                Date and time of a read in event
                Solar Object Locator of HEK database
                format: 'SOLyyyy-mm-ddThh:mm:ssL000C000'
            Outputs
            ------
            np.array
                Array with all subjects id's in the HEK event
        '''
        try:
            return np.asarray([x['subjectId'] for x in self.data if x['data']['#sol_standard'] == sol_standard])
        except:
            print('ERROR: sol_standard ' + str(sol_standard) +
                  ' could not be read from ' + self.file_name)
            return np.asarray([])

    def get_subjectdata_by_solstandard(self, sol_standard: str):
        '''
        Get an array of metadata for the subjects in the sol_standard HEK event
            Inputs
            ------
            sol_standard : str
                Date and time of a read in event
                Solar Object Locator of HEK database
                format: 'SOLyyyy-mm-ddThh:mm:ssL000C000'
            Outputs
            ------
            np.array
                Array with dict metadata for all subjects in the HEK event
        '''
        try:
            return np.asarray([x['data'] for x in self.data if x['data']['#sol_standard'] == sol_standard])
        except:
            print('ERROR: sol_standard ' + str(sol_standard) +
                  ' could not be read from ' + self.file_name)
            return np.asarray([])

    def get_subjectkeyvalue_by_solstandard(self, sol_standard: str, key: str):
        '''
            Get an array of key values of the subjects in the sol_standard HEK event
            Inputs
            ------
            sol_standard : str
                Date and time of a read in event
                Solar Object Locator of HEK database
                format: 'SOLyyyy-mm-ddThh:mm:ssL000C000'
            key : str 
                Dict key names 
                keys {'#file_name_0','#file_name_14', '#sol_standard', '#width','#height',
                    '#naxis1', '#naxis2', '#cunit1', '#cunit2','#crval1','#crval2', '#cdelt1', '#cdelt2', 
                    '#crpix1', '#crpix2', '#crota2', '#im_ll_x', '#im_ll_y','#im_ur_x', '#im_ur_y'}
            Outputs
            ------
            np.array
                Array with key value of the subjects in the HEK event
        '''
        try:
            if key == 'startDate' or key == 'endDate':
                return np.asarray([string_to_datetime(x['data'][key]) for x in self.data if x['data']['#sol_standard'] == sol_standard], dtype='datetime64')
            else:
                return np.asarray([x['data'][key] for x in self.data if x['data']['#sol_standard'] == sol_standard])
        except KeyError:
            print('ERROR: key ' + key + ' not found, please check your spelling')
        except:
            print('ERROR: sol_standard ' + str(sol_standard) +
                  ' could not be read from ' + self.file_name)
            return np.asarray([])

    def get_subjectid_by_dates(self, start_date: str, end_date: str):
        '''
            Get an array of subject id in a given timeframe
            Inputs
            ------
            start_date : str
                start of wanted time frame format 'YYYY-MM-dd' 
            end_date : str
                end of wanted time frame format 'YYYY-MM-dd' 

            Outputs
            ------
            np.array
                Array with all subjects id's occuring in given timeframe
        '''

        try:
            S, E = string_to_datetime(start_date), string_to_datetime(end_date)
            return np.asarray([x['subjectId'] for x in self.data if S < string_to_datetime(x['data']['startDate']) < E])
        except ValueError:
            print('ERROR: the start_date and end_date should be in format \'YYY-MM-dd\' or \'YYYY-MM-dd\' hh:mm:ss')
        except:
            print('ERROR: no data can be found between ' +
                  str(start_date) + str(end_date) + ' in ' + self.file_name)
            return np.asarray([])

    def get_subjectdata_by_id(self, subject: int):
        '''
        Get an array of metadata for the subject 
            Inputs
            ------
            subject: int
                Zooniverse subject ID
            Outputs
            ------
            np.array
                Array with dict metadata for the subject
        '''
        try:
            response = np.asarray([x['data'] for x in self.data if x['subjectId'] == subject])
            if len(response) == 1:
                return response[0]
            else:
                print('ERROR: subjectId ' + str(subject) +
                      ' is occuring more than once in ' + self.file_name)
                return np.asarray([])
        except:
            print("ERROR: could not load data from file: " + self.file_name)

    def get_subjectkeyvalue_by_id(self, subject: int, key: str):
        '''
            Get an array of key values of a subject
            Inputs
            ------
            subject: int
                Zooniverse subject ID
            key : str 
                Dict key names 
                keys {'#file_name_0','#file_name_14', '#sol_standard', '#width','#height',
                    '#naxis1', '#naxis2', '#cunit1', '#cunit2','#crval1','#crval2', '#cdelt1', '#cdelt2', 
                    '#crpix1', '#crpix2', '#crota2', '#im_ll_x', '#im_ll_y','#im_ur_x', '#im_ur_y'}
            Outputs
            ------
            value
                key value of the subject
        '''
        try:
            if key == 'startDate' or key == 'endDate':
                return np.asarray([string_to_datetime(x['data'][key]) for x in self.data if x['subjectId'] == subject], dtype='datetime64')[0]
            else:
                return np.asarray([x['data'][key] for x in self.data if x['subjectId'] == subject])[0]
        except KeyError:
            print('ERROR: key ' + key + ' not found, please check your spelling')
        except:
            print('ERROR: subjectId ' + str(subject) + ' could not be read from ' + self.file_name)
            return np.asarray([])

    def get_subjectkeyvalue_by_list(self, subjectidlist: np.array, key: str):
        '''
            Get an array of key values of the subjects in the sol_standard HEK event
            Inputs
            ------
            subjectidlist : np.array
                list with Zooniverse subject id's
            key : str 
                Dict key names 
                keys {'#file_name_0','#file_name_14', '#sol_standard', '#width','#height',
                    '#naxis1', '#naxis2', '#cunit1', '#cunit2','#crval1','#crval2', '#cdelt1', '#cdelt2', 
                    '#crpix1', '#crpix2', '#crota2', '#im_ll_x', '#im_ll_y','#im_ur_x', '#im_ur_y'}
            Outputs
            ------
            np.array
                Array with key value of the subjects in the subjectidlist
        '''
        try:
            if key == 'startDate' or key == 'endDate':
                return np.asarray([[string_to_datetime(x['data'][key]) for x in self.data if x['subjectId'] == subjectId][0] for subjectId in subjectidlist], dtype='datetime64')
            else:
                return np.asarray([[x['data'][key] for x in self.data if x['subjectId'] == subjectId][0] for subjectId in subjectidlist])
        except KeyError:
            print('ERROR: key ' + key + ' not found, please check your spelling')
        except:
            print('ERROR: subjectId ' + str(subjectidlist) +
                  ' could not be read from ' + self.file_name)
            return np.asarray([])
        
        
        
        
    def get_subjectid_by_JetCluster(self, list_jet_clusters, shj_id: str):
        '''
        Get an array of subject id in the Jet_Cluster identified by shj_id
            Inputs
            ------
            list_jet_clusters : list
                List of Jet_cluster objects to search
                can be read from a Jet_cluster.json file

            shj_id : str 
                The Jet_Cluster identifier to get the information for

            Outputs
            ------
            np.array
                Array with all subjects id's in the Jet_cluster with shj_id
        '''
        try:
            Jet = [list_jet_clusters[i] for i in range(2) if list_jet_clusters[i].ID == shj_id][0]
            return np.asarray([Jet.jets[i].subject for i in range(len(Jet.jets))])
        except:
            print('ERROR: shj_identifier ' + str(shj_id) +
                  ' could not be read from the list_jet_clusters input')
            return np.asarray([])

    def get_subjectdata_by_JetCluster(self, list_jet_clusters, shj_id: str):
        '''
        Get an array of metadata for the subjects in the Jet_Cluster identified by shj_id
            Inputs
            ------
            list_jet_clusters : list
                List of Jet_cluster objects to search
                can be read from a Jet_cluster.json file

            shj_id : str 
                The Jet_Cluster identifier to get the information for

            Outputs
            ------
            np.array
                Array with dict metadata for all subjects in the Jet_cluster with shj_id
        '''
        subjects_list = self.get_subjectid_by_JetCluster(list_jet_clusters, shj_id)
        return np.asarray([self.get_subjectdata_by_id(subject) for subject in subjects_list])
    

    def get_subjectkeyvalue_by_JetCluster(self, list_jet_clusters, shj_id: str, key: str):
        '''
            Get an array of key values of the subjects in the Jet_Cluster identified by shj_id
            Inputs
            ------
            list_jet_clusters : list
                List of Jet_cluster objects to search
                can be read from a Jet_cluster.json file

            shj_id : str 
                The Jet_Cluster identifier to get the information for
            key : str 
                Dict key names 
                keys {'#file_name_0','#file_name_14', '#sol_standard', '#width','#height',
                    '#naxis1', '#naxis2', '#cunit1', '#cunit2','#crval1','#crval2', '#cdelt1', '#cdelt2', 
                    '#crpix1', '#crpix2', '#crota2', '#im_ll_x', '#im_ll_y','#im_ur_x', '#im_ur_y'}
            Outputs
            ------
            np.array
                Array with key value of the subjects in the Jet_cluster with shj_id
        '''
        subjects_list = self.get_subjectid_by_JetCluster(list_jet_clusters, shj_id)
        return self.get_subjectkeyvalue_by_list(subjects_list, key)
    



def string_to_datetime(datetimestring: str):
    '''
        Construct a date from a string in ISO 8601 format.
        Inputs
        ------
        datetimestring: str 
            datetime str value to be converted from json format: 'YYYY-MM-dd hh:mm:ss'
            to datetime(YYYY,MM,dd,hh,mm,ss)
        Outputs
        ------
        datetime(YYYY,MM,dd,hh,mm,ss)
    '''
    return datetime.datetime.fromisoformat(datetimestring)