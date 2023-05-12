import os 
import re

filename = '/work/bb1153/b382075/datasets/MSWEP_V280/Past/Daily/1987121.nc'

def exctract_mem_size_and_unit(string):
      if 'K' in string:
            mem_unit = 'K'
      elif 'M' in string:
            mem_unit = 'M'
      elif 'G' in string:
            mem_unit = 'G'   
      elif 'T' in string:
            mem_unit = 'T'
      elif 'P' in string:
            mem_unit = 'P'  
      elif 'E' in string:
            mem_unit = 'E'      
      elif 'Z' in string:
            mem_unit = 'Z'     
      elif 'Y' in string:
            mem_unit = 'Y'             
      
      res = re.findall("\d+\.\d+", string)
      if res==[]:
            mem_size = int(re.findall("\d+", string)[0])
      else:
            mem_size = float(re.findall("\d+\.\d+", string)[0])
      return  mem_size, mem_unit


def mem_of_file(file = filename):
    with os.popen("du -sh " + str(file)) as f:
            _ = f.readline()
            memory_of_file = re.split('\t', _)[0]
            mem_size, mem_unit = exctract_mem_size_and_unit(memory_of_file)
            return  mem_size, mem_unit
    
def mem_unit_converter(old_unit='M', new_unit='G'):
        if old_unit=='K':
                if new_unit=="M":
                        return (1/1024)
                elif new_unit =="G":
                      return (1/1024)**2
                elif new_unit =="T":
                      return (1/1024)**3
                elif new_unit =="P":
                      return (1/1024)**4
                elif new_unit =="E":
                      return (1/1024)**5
                elif new_unit =="K":
                      return 1
        elif old_unit=='M':
              if new_unit=="K":
                    return (1024)
              elif new_unit =="G":
                    return (1/1024)
              elif new_unit =="T":
                    return (1/1024)**2
              elif new_unit =="P":
                    return (1/1024)**3
              elif new_unit =="E":
                    return (1/1024)**4
              elif new_unit=="M":
                    return 1
        elif old_unit=='G': 
              if new_unit=="K": 
                    return (1024)*2 
              elif new_unit=="M":
                    return (1024) 
              elif  new_unit=="T":
                    return (1/1024)
              elif new_unit=="P":
                    return (1/1024)**2
              elif new_unit =="E":
                    return (1/1024)**3
              elif new_unit == 'G':
                    return 1
        else:
                raise Exception("unknown type")

def exctract_sinfo(sinfo_str=' '):
    """_summary_

    Args:
        sinfo_str (str, optional): _description_. Defaults to ' '.

    Returns:
        _type_: _description_
    """    
    with os.popen(sinfo_str) as f:
            f.readline()
            f.readline()
            _ = f.readline()
    list_with_empty_strings= re.split(r'[\n ]', _)
    new_list = [x for x in list_with_empty_strings if x != '']
    return new_list
        
def max_resources_per_node(queue="compute"):
    """_summary_

    Args:
        queue (str, optional): _description_. Defaults to "compute".

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        _type_: _description_
    """    
    max_resources = exctract_sinfo("sinfo  --partition="+str(queue)+" -lNe")
    if max_resources[2]==queue:   
        max_cpus = max_resources[4]
        max_memory  = str(float(max_resources[6])/1024)+" GB"
        max_sockets, max_cores, max_threads = re.split(r'[:]', max_resources[5])
    else:
        raise Exception("The function can not extract information about the queue correctly. \n \
                        Please, select the amount of memory, cores, threads, and walltime manually.")

    if queue == exctract_sinfo("sinfo  --partition="+str(queue)+" -le")[0]:
        max_walltime = exctract_sinfo("sinfo  --partition="+str(queue)+" -le")[2]
    else:
        raise Exception("The function can not extract information about the queue correctly. \n \
                        Please, select the amount of memory, cores, threads, and walltime manually.")
    
    return  max_memory, max_walltime, max_cpus, max_sockets, max_cores, max_threads 



