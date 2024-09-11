#!/usr/bin/env python
# -*- coding: utf_8 -*-
""" downloaded from http://xbmc-addons.googlecode.com/svn/addons/ """
""" This is a modded version of the original addons.xml generator """

""" Put this version in the root folder of your repo and it will """
""" zip up all add-on folders, create a new zip in your zips folder """
""" and then update the md5 and addons.xml file """

""" Recoded Fby whufclee (info@totalrevolution.tv) """
""" Added FTP , external logging and writing non-ascii chars by FTG """

import re
import os
import shutil

import hashlib
import zipfile

############################
##FTP MOD##
import sys
import time
import ftplib
import os.path
from ftplib import FTP, error_perm
## logging
import logging
real_path = os.path.dirname(os.path.realpath(__file__)) + os.sep
LOG = real_path+'log.txt'
log_formatter=logging.Formatter('[%(asctime)-15s] %(message)s' ,"%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(LOG)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
try:
	if (logger.hasHandlers()):
		logger.handlers.clear()
except:
	pass
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.info('\n')
##Force CWD
os. chdir(real_path)
############################

os.system('cls')

####################! READ THIS !###########################
############## ENTER YOUR FTP INFO BELOW ###################
############################################################
#MUST HAVE / FOR FTP_DIR AND FTP_REPO_FOLDER AT THE END!####
#preferred to have the last folders like shown in FTP paths#
###It will create them if they are not found on Server######
############################################################


##FTP path for public Zips folder
FTP_DIR = '/path/of/ftp/folder/to/zips/'

##FTP path for public Repo folder
FTP_REPO_FOLDER = '/path/of/ftp/folder/to/repo/'

##FTP login info
HOST = 'addressofftp'
FTP_USERNAME = 'ftpusername'
FTP_PASSWORD = 'ftppassword'

###########################################################
###########################################################

class Generator:
	"""
		Generates a new addons.xml file from each addons addon.xml file
		and a new addons.xml.md5 hash file. Must be run from the root of
		the checked-out repo. Only handles single depth folder structure.
	"""
	def __init__(self):
# Create the zips folder if it doesn't already exist
		zips_path = ('zips')
		if not os.path.exists(zips_path):
			os.makedirs(zips_path)

# Comment out this line if you have .pyc or .pyo files you need to keep
		self._remove_binaries()

		self._generate_addons_file()
		self._generate_md5_file()
		logger.info("Finished updating addons xml and md5 files")

	def _create_zips(self, addon_id, version):
		xml_path = os.path.join(addon_id, 'addon.xml')
		addon_folder = os.path.join('zips', addon_id)
		if not os.path.exists(addon_folder):
			os.makedirs(addon_folder)
		else:
			shutil.rmtree(addon_folder)
			os.makedirs(addon_folder)

		final_zip = os.path.join('zips', addon_id, '{0}-{1}.zip'.format(addon_id, version))
		if not os.path.exists(final_zip):
			logger.info("NEW ADD-ON - Creating zip for: {0} v.{1}".format(addon_id, version))
			zip = zipfile.ZipFile(final_zip, 'w', compression=zipfile.ZIP_DEFLATED )
			root_len = len(os.path.dirname(os.path.abspath(addon_id)))
			
			ignore = ['.git', '.github', '.gitignore', '.DS_Store', 'thumbs.db', '.idea', 'venv']
			
			for root, dirs, files in os.walk(addon_id):
				# remove any unneeded git artifacts
				for i in ignore:
					if i in dirs:
						try:
							dirs.remove(i)
							logger.info("Removed Directory {0} in {1}".format(i,addon_id))
						except:
							pass
					for f in files:
						if f.startswith(i):
							try:
								files.remove(f)
								logger.info("Removed File {0} in {1}".format(i,addon_id))
							except:
								pass
				
				archive_root = os.path.abspath(root)[root_len:]

				for f in files:
					fullpath = os.path.join(root, f)
					archive_name = os.path.join(archive_root, f)
					zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
					logger.info("Zipping {0}".format(archive_name))
			
			zip.close()
			
			# Copy over the icon, fanart and addon.xml to the zip directory
			copyfiles = ['icon.png', 'fanart.jpg', 'addon.xml']
			files = os.listdir(addon_id)
			for file in files:
				if file in copyfiles:
					shutil.copy(os.path.join(addon_id, file), addon_folder)
					logger.info("Copied File {0} for Addon {1}".format(file,addon_id))

# Remove any instances of pyc or pyo files
	def _remove_binaries(self):
		for parent, dirnames, filenames in os.walk('.'):
			for fn in filenames:
				if fn.lower().endswith('pyo') or fn.lower().endswith('pyc'):
					compiled = os.path.join(parent, fn)
					py_file = compiled.replace('.pyo', '.py').replace('.pyc', '.py')
					if os.path.exists(py_file):
						try:
							os.remove(compiled)
							logger.info("Removed compiled python file:")
							logger.info(compiled)
							logger.info('-----------------------------')
						except:
							logger.info("Failed to remove compiled python file:")
							logger.info(compiled)
							logger.info('-----------------------------')
					else:
						logger.info("Compiled python file found but no matching .py file exists:")
						logger.info(compiled)
						logger.info('-----------------------------')

	def _generate_addons_file(self):
		# addon list
		addons = os.listdir('.')

		# final addons text
		addons_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"

		# loop thru and add each addons addon.xml file
		for addon in addons:
			try:
				if not os.path.isdir(addon) or addon == "zips" or addon.startswith('.'):
					continue
				_path = os.path.join(addon, "addon.xml")
				xml_lines = open( _path, "r",  encoding="utf8" ).read().splitlines()
				addon_xml = ""

				# loop thru cleaning each line
				ver_found = False
				for line in xml_lines:
					if line.find( "<?xml" ) >= 0:
						continue
					if 'version="' in line and not ver_found:
						version = re.compile('version="(.+?)"').findall(line)[0]
						ver_found = True
					addon_xml += line.rstrip() + "\n"
				addons_xml += addon_xml.rstrip() + "\n\n"

				# Create the zip files				  
				self._create_zips(addon, version)

			except Exception as e:
				logger.error("Excluding {0} for {1}".format(_path, e))

		# clean and add closing tag
		addons_xml = addons_xml.strip() + "\n</addons>\n"
		self._save_file(addons_xml.encode('utf-8'), file=os.path.join('zips', 'addons.xml'), decode=True)

	def _generate_md5_file(self):
		
		try:
			m= hashlib.md5(open(os.path.join('zips', 'addons.xml'), 'r',  encoding="utf8" ).read().encode('utf-8')).hexdigest()
			self._save_file(m, file=os.path.join('zips', 'addons.xml.md5'))
		except Exception as e:
			logger.error("An error occurred creating addons.xml.md5 file!\n{0}".format(e))
	
	def _save_file(self, data, file, decode=False):
		try:
			if decode:
				open(file, 'w',encoding='utf-8').write(data.decode('utf-8'))
				logger.info("File {0} written".format(file))
			else:
				open(file, "w" ).write(data)
				logger.info("File {0} written".format(file))
		except Exception as e:
			logger.error("An error occurred saving {0} file!\n{1}".format(file, e))

######## FTG MOD TO GIT & FTP Zips /Public Repo Folder ###################
##########################################################################
####################### DONT MODIFY BELOW! ###############################
ftp_site = {'pass': FTP_PASSWORD,'user': FTP_USERNAME,'site': HOST}
LOCAL_REPO_DIR =os.getcwd()+'\\repo\\'
LOCAL_DIR = os.getcwd()+'\\zips\\'

def get_files(root_path, recursive = True):
	l = []
	if recursive:
		for root, dirs, files in os.walk(root_path, topdown = True):
			l += [os.path.join(root, i) for i in files]
	else:
		l = os.listdir(root_path)
	return l

class FtpPathCache():
	def __init__(self, ftp_h):
		self.ftp_h = ftp_h
		self.path_cache = []

	def ftp_exists(self, path):
		exists = None
		if path not in self.path_cache:
			try:
				self.ftp_h.cwd(path)
				exists = True
				self.path_cache.append(path)
			except ftplib.error_perm as e:
				if str(e.args).count('550'):	
					exists = False
		else:
			exists = True
		return exists

	def ftp_mkdirs(self, path, sep='/'):
		split_path = path.split(sep)
		new_dir = ''
		for server_dir in split_path:
			if server_dir:
				new_dir += sep + server_dir
				if not self.ftp_exists(new_dir):
					try:
						logger.info("Create directory {0}".format(new_dir))
						self.ftp_h.mkd(new_dir)
					except Exception as e:
						logger.error("ERROR Creating directory {0}: {1} -- {2} ".format(new_dir, str(e.args)))

def transfer_files(list_files, ftp_site, root_folder, destination_folder):
	pass_ = None
	if(('pass' not in ftp_site) or (ftp_site['pass'] is None)):
		raise Exception('the password should be provided')

	pass_ = ftp_site['pass']
	ftp = None

	try:
		ftp = ftplib.FTP(ftp_site['site'], ftp_site['user'], pass_)
	except Exception as e:
		logger.error("An exception occurred during the connection to {0}@{1} : verify the connection parameters".format(ftp_site['user'], ftp_site['site']))
		raise e

	root_folder = os.path.abspath(root_folder) if root_folder is not None else None

	# first slash is important
	destination_folder = '/' + destination_folder.rstrip('\\').strip('/') + '/' if destination_folder is not None else ""

	ftp_cache = FtpPathCache(ftp)
	if not ftp_cache.ftp_exists(destination_folder):
		ftp_cache.ftp_mkdirs(destination_folder)

	current_remote = ftp.pwd()

	for f in list_files:

		# local path
		f = os.path.abspath(f)
		relative_path_to_root = os.path.relpath(os.path.dirname(f), root_folder) if root_folder is not None else f

		logger.info("sending file: {0}".format( os.path.join(relative_path_to_root, os.path.basename(f))))

		# remote directory
		remote_path = os.path.join(destination_folder, relative_path_to_root if relative_path_to_root != '.' else "")

		if not ftp_cache.ftp_exists(remote_path):
			ftp_cache.ftp_mkdirs(remote_path)

		# Change the directory if needed
		if current_remote != remote_path:
			try:
				ftp.cwd('/' + remote_path.rstrip('/'))
				current_remote = remote_path
				continue_on = True
			except ftplib.error_perm as e:
				logger.error("[ftp] CWD ERROR on path {0} -- {1}".format(ftp.pwd(), str(e.args)))
				ftp.retrlines('LIST')
				continue

		ftp_command = 'STOR %s' % os.path.basename(f)
		logger.debug('[ftp] command {0}'.format(ftp_command))
		ftp.storbinary(ftp_command, open(f, 'rb'))

	ftp.retrlines('LIST')
	return

def ftp_upload():
	root = os.path.expanduser(LOCAL_DIR)
	list_of_files = get_files(root)
	destination_folder = '/' + FTP_DIR
	logger.info("# files to transfer: {0}".format(len(list_of_files)))

	def remote_files(l, filename):
		return [i for i in l if os.path.basename(i).lower() != filename]

	list_of_files = remote_files(list_of_files, os.path.basename(__file__))
	transfer_files(list_of_files, ftp_site, LOCAL_DIR, destination_folder)

def git_upload():
	os.system('@echo off')
	os.system('git add .')
	os.system('set /p commitmessage=Please enter commit message ')
	os.system('git commit -m "%commitmessage%"')
	os.system('git push')


####Make Public Repo Folder and files
def make_repo_folder():
	if not os.path.exists('repo'):
		os.makedirs('repo')
	else:
		shutil.rmtree('repo')
		os.makedirs('repo')
	#place repo zip in repo folder
	for root, dirs, files in os.walk(os.getcwd()+'\\zips\\'):
		for file in files:
			if file.startswith('repository') and file.endswith('.zip'):
				shutil.copy(os.path.join(root, file), 'repo')
				logger.info('[Repo Zip]: {0}'.format(file))
	
	#robots.txt
	robot = open("repo\\robots.txt", "w")
	robot.write("""User-agent: *
Disallow: /
""")
	robot.close
	#.htacess
	htacess = open("repo\\.htaccess","w")
	htacess.write("""Options +Indexes""")
	htacess.close
	#index.html
	index= open("repo\\index.php","w")
	index.write("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<head>
<meta name="robots" content="noindex,nofollow">
</head>
<html>
  <body>
 <h1>Index of <? echo basename(__DIR__) ?></h1>
<hr>

<table>
  <thead>
        <tr>
          <th>Filename</th>
          <th>Type</th>
          <th>Size <small>(bytes)</small></th>
          <th>Date Modified</th>
        </tr>
  </thead>
  <tbody>
  <?php
     //logging errors//
     error_reporting(E_ALL | E_STRICT);
     ini_set('display_errors', false);
     ini_set('log_errors', false);
     ini_set('error_log','error_log.txt');
     //

    function ConvertSize($bytes){
       if ($bytes >= 1073741824){$bytes = number_format($bytes / 1073741824, 2) . ' GB';
       }elseif ($bytes >= 1048576){$bytes = number_format($bytes / 1048576, 2) . ' MB';
       }elseif ($bytes >= 1024){$bytes = number_format($bytes / 1024, 2) . ' KB';
       }elseif ($bytes > 1){$bytes = $bytes . ' bytes';
       }elseif ($bytes == 1){$bytes = $bytes . ' byte';
       }else{$bytes = '0 bytes';
       }
       return $bytes;
       }
    // Opens directory
    $myDirectory=opendir(".");
    
    // Gets each entry
    while($entryName = readdir($myDirectory)) {
     $pathinfo = pathinfo($entryName);
     if ($pathinfo['extension'] != 'html')
      if ($pathinfo['extension'] != 'php')
       //if($entryName != 'add_another_file_to_skip.ext')
        $dirArray[] = $entryName;
}
    
    // Finds extensions of files
    function findexts ($filename) {
      $filename=strtolower($filename);
      $exts=substr($filename, strrpos($filename, '.')+1);
      return $exts;
    }
    
    // Closes directory
    closedir($myDirectory);
    
    // Counts elements in array
    $indexCount=count($dirArray);
    
    // Sorts files
    sort($dirArray);
    
    // Loops through the array of files
    for($index=0; $index < $indexCount; $index++) {
    
      // hides .   and  ..  
      $hide=".";

      if(substr("$dirArray[$index]", 0, 1) != $hide) {
      
      // Gets File Names
      $name=$dirArray[$index];
      $namehref=$dirArray[$index];
      
      // Gets Extensions 
      $extn=findexts($dirArray[$index]); 
      
      // Gets file size 
      $size=ConvertSize(filesize($dirArray[$index]));
      
      // Gets Date Modified Data
      $modtime=date("M j Y g:i A", filemtime($dirArray[$index]));
      
      // Adds better ext names
      switch ($extn){
        case "png": $extn="PNG Image"; break;
        case "jpg": $extn="JPEG Image"; break;
        case "svg": $extn="SVG Image"; break;
        case "gif": $extn="GIF Image"; break;
        case "ico": $extn="Windows Icon"; break;
        
        case "txt": $extn="Text File"; break;
        case "log": $extn="Log File"; break;
        case "js": $extn="Javascript"; break;
        case "css": $extn="Stylesheet"; break;
        case "pdf": $extn="PDF Document"; break;
        
        case "zip": $extn="ZIP Archive"; break;
        case "bak": $extn="Backup File"; break;
        
        default: $extn=strtoupper($extn)." File"; break;
      }
      
      // Separates directories
      if(is_dir($dirArray[$index])) {
        $extn="&lt;Directory&gt;"; 
        $size="&lt;Directory&gt;"; 
        $class="dir";
      } else {
        $class="file";
      }
      
      // Print 'em
      print("
      <tr>
        <td><a href=\\"$namehref\\">$name</a></td>
        <td>$extn</td>
        <td>$size</td>
        <td>$modtime</td>
      </tr>");
      }
    }
  ?>
  </tbody>
</table>
</pre><hr><address>Proudly Served by Yours Truly Web Server at this place Port 8080</address>
</body>
</html>
""")
	index.close

def ftp_repo_files():
	#locates all files in the repo folder and ftp them
	root = os.path.expanduser(LOCAL_REPO_DIR)
	logger.info('root: {0}'.format(root))
	list_of_files = get_files(root)
	destination_folder = '/' + FTP_REPO_FOLDER
	logger.info('Files to upload in Repo: {0}'.format(list_of_files))
	transfer_files(list_of_files, ftp_site, LOCAL_REPO_DIR, destination_folder)

###Stiil needs work
def old_repo_zip():
	try:
		ftp = ftplib.FTP(ftp_site['site'], ftp_site['user'], ftp_site['pass'])
	except Exception as e:
		logger.error("An exception occurred during the connection to {0}@{1} : verify the connection parameters".format(ftp_site['user'], ftp_site['site']))
		raise e
	### See if Host repo folder has a zip already
	data = []
	ftp.dir(FTP_REPO_FOLDER, data.append)
	
	for file in data:
		vars = file.split(maxsplit = 9)
		name = vars[8]
		time_str = vars[5] + " " + vars[6] + " " + vars[7]
		x = name.split(".")
		formats=["zip"]
		if x[-1] in formats:
			logger.info('Zip File Found: {0} - {1}'.format(name, str(time_str)))
###

#############################################################################

print((30 * '-'))
print ("  THE Repo Generator with FTP upload ")
print((30 * '-'))
print ("  Help:")
print ("  Make sure you have modified the FTP items in the script if you are FTPing")
print ("  Generate Repo - Takes all plugin folders and generates Kodi friendly")
print ("                  Repositories with MD5 and addon.xml.")
print ('  Generate Public Repo - Creates "repo" folder, places your Repository')
print ("                  zip there & creates a index.html & .htaccess for it.")
print ('  FTP - Uploads your files to your host')
print((30 * '-'))
print ("  1. Generate Repo & Generate Public Repo & FTP")
print((30 * '-'))
print ("  2. Generate Repo")
print ("  3. Generate Repo & FTP")
print((30 * '-'))
print ("  4. Generate Public Repo")
print ("  5. Generate Public Repo & FTP")
print((30 * '-'))


choice = input('  Enter [1 - 5] : ')
choice = int(choice)

try:
	if choice == 1:
			print ("Starting the Zipping...")
			Generator()
			print ("Zipping Completed...")
			print ("Starting the FTP upload...")
			ftp_upload()
			print ("FTP upload Completed...")
			print ("Making the Repo Folder & Files...")
			make_repo_folder()
			print ("Uploading the Repo Files...")
			ftp_repo_files()
			print ("Process Completed...")
	elif choice == 2:
			print ("Starting the Zipping...")
			Generator()
			print ("Process Completed...")
	elif choice == 3:
			print ("Starting the Zipping...")
			Generator()
			print ("Zipping Completed...")
			print ("Starting the FTP upload...")
			ftp_upload()
			print ("FTP upload Completed...")
			print ("Process Completed...")
	elif choice == 4:
			print ("Starting the Zipping...")
			Generator()
			print ("Zipping Completed...")
			print ("Making the Public Repo Folder & Files...")
			make_repo_folder()
			print ("Process Completed...")
	elif choice == 5:
			print ("Starting the Zipping...")
			Generator()
			print ("Zipping Completed...")
			print ("Making the Public Repo Folder & Files...")
			make_repo_folder()
			print ("Uploading the Public Repo Files...")
			ftp_repo_files()
			logger.info('Please remove the old zip files manually from your repo folder on your Host.')
			print ("Process Completed...")
	else:
		print ("Invalid Choice. Try again...")

except Exception as e:
	logger.error("[-]Error Detected: {0}".format(str(e)))

print()
os.system("pause")