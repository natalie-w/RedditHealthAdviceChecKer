import React, { Component,useState, useEffect } from "react";
import {Button, Modal, Checkbox} from 'antd'
import "./instructions.css";

function InstructionsContainer() {

    
    const [task, setTask] = useState(0);

    // TODO: make something here in training
    const training = () => {
        let path = '/#/Training';
        window.location.assign(path);
    }

    const redditComments = () => {
        let path = '/#/Task1A';
        window.location.assign(path);
    }

    const modelDemo = () => {
        let path = '/#/Task1B';
        window.location.assign(path);
    }

    // connect with the backend to randomize the task 
    useEffect(() => {
        fetch('http://localhost:8080/setup')
        .then(response => response.json())
        .then(data => {
            console.log(data)
            console.log(data['task_number']);
            setTask(data['task_number']);
            // send user id as well
            localStorage.setItem('user-id', data['user_id']);
            console.log(localStorage)
        });
    }, []);


    return (
      <div className="container">
        <h1>Experiment Home Page</h1> 

        Please select the button your proctor tells you to to begin your user test.

        <div className="text"> 
            <Button variant="btn btn-success" onClick={training}>
                Training
            </Button>
        </div>

        <div className="text"> 
            <Button variant="btn btn-success" onClick={redditComments}>
                Reddit Comments
            </Button>
        </div>

        <div className="text"> 
            <Button variant="btn btn-success" onClick={modelDemo}>
                Model Demo
            </Button>
        </div>

      </div>
      );
}

export default InstructionsContainer;