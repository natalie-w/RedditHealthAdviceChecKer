import React, { useEffect, useState } from "react";
import './style.css'


// this is how you create a separate component
function PredictionContainer({ currentPrediction }) {
    // store the prediction message to display 
    const [predMessage, setPredMessage] = useState("");


    useEffect(() => {
        setPredMessage("Example: The AI assistant suggests this image corresponds to a(n) ")
    }, []);


    return (
        <div className="column-container">
            <div className="prediction-container">
                <div className="text"> 
                    You can create boxes to separate some information
                    <p> {predMessage} <b> {currentPrediction} </b>   </p>
                </div>
            </div> 
        </div>
    )
}

export default PredictionContainer;