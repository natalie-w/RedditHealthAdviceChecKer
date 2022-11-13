import {React, useEffect, useState} from 'react';
import ReactDOM from 'react-dom';
import { useParams } from "react-router-dom";
import {
  Form,
  Select,
  // Radio,
  // Input,
  Button,
  Radio,
} from 'antd';
import './survey.css'
const { Option } = Select;



const formItemLayout = {
    labelCol: {
        span: 22,
        offset:1
    },
    wrapperCol: {
        span: 30,
        offset:1
    },
};

const SurveyContainer = () => {
  const [form] = Form.useForm();
  const [answers, setAnswers] = useState({});


  const onFinish = (values) => {
    console.log('Received values of form: ', values);
    let copySaveArray = values
    setAnswers(values)
    // save data
    let data = {
        user_id: localStorage.getItem("user-id"),
        q1: 1, 
        q2: 2,
    };
    sendData(data)
    let path = '/#/End'; 
    window.location.assign(path);
  };

  const sendData = (obj) => {
    fetch('http://localhost:8080/surveyData', {
      method: 'POST',
      body: JSON.stringify(obj),
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    }).then(response => response.json())
      .then(message => {
        console.log(message)
        // getLastestTodos();
      })
  } 

  function newTabFinalSurvey() {
        window.open(
        "https://forms.gle/Vqqq2YsG55NiFhrQ6", "_blank");
    }



  return (
    <div className="container"> 

        <div className="title"> Study Survey</div>
        <div className='text'> Thank you for your time. Please complete this post-survey about our bot.</div>
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfjF5eLbkE6zgYfQ_r-o7KIOj6zopytRvlCqCOfA9RjryxGqg/viewform?embedded=true" width="640" height="902" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
    </div>

    
    
  );
};
export default SurveyContainer;