import React, { Component, useState, useEffect } from "react";
import { Button, Modal } from 'antd'
import "antd/dist/antd.css";
import "./main.css";

function Main2Container() {

    const [text, setText] = useState("");
    const [imageData, setImageData] = useState([]);
    const [currentImage, setCurrentImage] = useState("");
    const [currentPrediction, setCurrentPrediction] = useState("");
    const [visible, setVisible] = useState(false);
    const [imageCount, setImageCount] = useState(0);
    const [taskTime, setTaskTime] = useState((Date.now() + 1000 * 1000));
    const [currentTime, setCurrentTime] = useState(0);
    const [moveToSurvey, setMoveToSurvey] = useState(false);
    const [render, setRender] = useState(false);

    let totalImages = 3;
    const baseImgUrl = "./";

    const routeChange = () =>{ 
        let path = '/#/Survey'; 
        window.location.assign(path);

    }

    const onChangeInput = e => {
        setText(e.target.value);
    };

    const handleDisplayInfo=()=>{
        console.log('opening popup')
        setVisible(true);
    };
    
    const handleCancel = () => {
        setVisible(!visible);
    };


    const nextChange = () =>{
        if (text==="") {
            alert("Please make sure to complete all the fields!");
        } else {
            let count = imageCount + 1;
            if (count >= totalImages) {
                console.log('done with images')
                setMoveToSurvey(true);
            } else {
                // reinitialize variables
                console.log("moving to next image")
                setText(""); 
                setImageCount(count);
                setCurrentImage(imageData[count].name);
                setCurrentPrediction(imageData[count].label);
                setTaskTime(Date.now())
            }
        }
    }

    // testing communication with backend
    useEffect(() => {
        fetch('http://0.0.0.0:8080/time').then(res => 
        res.json()).then(data => {
            setCurrentTime(data.time);
            console.log(data.time)
        });
        }, []);
    

    // initialize image
    useEffect(() => {
        console.log('getting images')
        fetch('http://localhost:8080/imageInfo')
        .then(response => response.json())
        .then(data => {
            console.log(data['imgs']);
            setImageData(data['imgs']);
            let image_name = data['imgs'][0].name
            setCurrentImage(image_name)
            console.log(image_name)
            setCurrentPrediction(data['imgs'][0].label);
            setRender(true);
            setTaskTime(Date.now())
        });
    }, []);    


    return (
      <>
       {render ?

            <div className="container">
            <div className="title">Main experiment</div>
            <div className="column-container"> 
            <div className="left-column"> 
                <p> This is how you load an image:</p>
                <div className="img-frame">
                    <img className="image-inner" src={baseImgUrl + currentImage}/>
                </div>
                <p> {imageCount + 1} / {totalImages} Images</p>
            </div>

            <div className="right-column"> 
                <div className="instr">
                    <t> See more functionalities in this task:</t>
                </div>
            

                <Button className="btn-2" onClick={handleDisplayInfo}>
                    Open pop-up window
                </Button>
                <Modal
                    visible={visible}
                    title="Additional information"
                    centered
                    footer={null}
                    onCancel={handleCancel}
                >
                    <div className="pop-container">
                        This is how you add a pop-up window

                    </div>
                </Modal>



                <div className="instr">
                    <t> This is how you create a text box:</t>
                </div>
                <input
                    type="text"
                    value={text}
                    onChange={onChangeInput}
                />
                <div className="instr">
                    Note: we are not saving any information in this task. Refer to the other task to learn how to retrieve responses. 
                </div>
                <div className="button-container"> 
                    <Button variant="btn btn-success"  style={{marginLeft:"70%"}}  onClick={nextChange}>
                        Next
                    </Button>
                </div>
            </div>
            </div>

            {(moveToSurvey) && 
            <div className="button-container"> 
                <Button disabled={!moveToSurvey} variant="btn btn-success" onClick={routeChange}>
                    Survey
                </Button>
            </div>
            }

            </div>

        :
            <> 
            <h1> Loading ...</h1>
            </>
        }
      </>
       
      );
}

export default Main2Container;