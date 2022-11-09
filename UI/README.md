## Template for designing your user experience

This template uses React to build the frontend and Flask in the backend. The overall structure was created to support a user study from a starting page followed by instructions, the main experiment, and a final survey. Chrome is recommended. 

## Getting Started
You can directly clone this repository and follow these steps to launch the web application. 

### Prerequisites
First, you need to install NodeJS and NPM from the website: [https://nodejs.org/en/](https://nodejs.org/en/). 

### Installation
1. Install all the packages neeeded for the frontend. Run the following line in the project directory. This will create a folder called node_modules
   ```sh
   npm install
   ```

2. Go into the api/ folder and activate the virtual environment (myvenv)
   ```sh
   source myvenv/bin/activate
   ```

**Note**: you need this version of Flask SQLAlchemy:
   ```sh
   pip install flask_sqlalchemy==2.5.1
   ```

3. In the api/ folder, create a folder to store the database
   ```sh
   mkdir tmp
   ```

4. To keep the backend on, run the following line in the api/ folder:
   ```sh
   python api.py
   ```
**Note**: This will create the database and it will appear in the tmp folder (`test.db`). 

**Note**: You can copy this link in a browser [http://0.0.0.0:8080/time](http://0.0.0.0:8080/time) to make sure that the backend is running. You can change the endpoint to visualize different outcomes (check the endpoints in the api.py script). 

5. In another terminal tab, go to the src/ folder to launch the frontend using the following line:
   ```sh
   npm start
   ```
**Note**: this will open a browser or you can open [http://localhost:3000/#/](http://localhost:3000/#/) to view it. 

**Note**: You can open the browser console (right click-Inspect-Console) to visualize log messages or errors from the frontend. 

The application supports two tasks (chosen randomly). If you want to learn how to send data to the backend, you should follow the process in task 1 at: [http://localhost:3000/#/Main1](http://localhost:3000/#/Main1). 