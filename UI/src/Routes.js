
import React, { Component } from "react";
import { HashRouter, Router, Switch, Route} from 'react-router-dom';

import StartContainer from './pages/start/start';
import InstructionsContainer from './pages/instr/instructions';
import Task1AContainer from "./pages/main/A/task1";
import Main1Container from "./pages/main/main-task1";
import Main2Container from "./pages/main/main-task2";
import SurveyContainer from "./pages/survey/survey"
import EndContainer from "./pages/end/end";


export default class Routes extends Component {
    render() {
        return (
            <HashRouter>
                <Switch>
                    <Route path="/" exact component={StartContainer} />
                    <Route path="/Instructions" component={InstructionsContainer} />
                    <Route path="/Task1A" component={Task1AContainer} />
                    <Route path="/Main1" component={Main1Container} />
                    <Route path="/Main2" component={Main2Container} />
                    <Route path="/Survey" component={SurveyContainer} />
                    <Route path="/End" component={EndContainer} />

                </Switch>
            </HashRouter>

        )
    }
}