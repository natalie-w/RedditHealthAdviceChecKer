import React, { useEffect, useState } from "react";
import {Button} from 'antd'
import './style.css'


// this is how you create a separate component
function PredictionContainer({ currentPrediction }) {
    // store the prediction message to display 
    const [predMessage, setPredMessage] = useState("");
    console.log('curr pred', currentPrediction)
    var renderedOutput = currentPrediction.split('/n').map(item => <div> <b> {item} </b> </div>);

    const handlePredict=()=>{
        return true;
    };



    useEffect(() => {
        setPredMessage("")


    }, []);

    console.log("inside prediction containers")
    console.log(currentPrediction)
    console.log(currentPrediction.split('/n'))

    return (
        <div className="column-container">
            <div className="prediction-container">
                <div className="text"> 
                    The bot responds with:

                    <div>
                        {renderedOutput}
                    </div>
                </div>
            </div> 
        </div>
    )
}

export default PredictionContainer;