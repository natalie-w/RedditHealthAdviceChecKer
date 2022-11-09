import React, { Component,useState } from "react";
import {Button, Modal} from 'antd'
// import { useHistory} from "react-router";

import "./start.css";

function StartContainer() {
    // let history = useHistory();
    const [agree, setAgree] = useState(false);

    const checkboxHandler = () => {
      setAgree(!agree);
    }
  
    const routeChange = () =>{ 
      let path = '/#/Instructions'; 
      // history.push(path);
      window.location.assign(path);
      console.log('moving to instructions page')
    }

    return (
      <div className="Home">
        <div className="lander">
            <h1>Study title here</h1>
            <p> This is the start page. Welcome to our study. </p>

            <div>
                <input type="checkbox" id="agree" onChange={checkboxHandler} />
                <label htmlFor="agree"> I agree to the <b>terms and conditions</b></label>
            </div>

            <Button disabled={!agree} variant="btn btn-success" onClick={routeChange}>
                Continue
            </Button>
        </div>
      </div>
      );
}

export default StartContainer;