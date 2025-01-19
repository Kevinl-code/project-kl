pip install virtualenv
cd /path/to/your/desired/folder
python -m venv venv_name      ( (venv_name) - Custom name)

#For example:
 python -m venv myenv

  This will create a folder named `myenv` in your desired directory containing the virtual environment.

#Activate the Virtual Environment
   Once you’ve created your virtual environment, you need to activate it.

venv_name\Scripts\activate

   Once activated, your prompt should show the environment name `(venv)` like this:

(venv) C:\path\to\your\project>

pip install flask matplotlib requests pandas numpy
pip list
pip freeze > requirements.txt
pip install -r requirements.txt
Updating `pip` (Optional)

#If you want to make sure you have the latest version of `pip`, you can update it by running:
 pip install --upgrade pip
 
