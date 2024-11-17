import { useState, useRef } from 'react';
import './App.css';

import { v4 as uuidv4 } from 'uuid';

import Message from './components/Message';
import MessageLog from './components/MessageLog';

// Unique id for this session
export const sid = uuidv4();

// Root URL for API requests
export const root_url = "http://127.0.0.1:5001/api/v1";

function App() {

  const [messages, setMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [toggleLogs, setToggleLogs] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [checkpoints, setCheckpoints] = useState([]);
  const [input, setInput] = useState("")
  const inputRef = useRef(null);


  // Example prompts showcasing different capabilities of model
  const exPrompts = [
    // "When was the warmest day of 2023?",
    // "What is the average temperature for April 1st in each year since 2010?",
    // "What proportion of days in March are, on average under 30 degrees, 30-50 degrees, 50-70, and 70+ degrees?",
    // "What was the average rainfall for 2023?",
    // "What was the coldest day between October and November 2016?",
    // "What is the average temperature in January since 2020?",
    // "Which day had the most snow in 2021?",
    // "What was the highest temperature of each month in 2022?",
    // "What is the coldest weekday on average in the past year?",
    // "What is the proportion of days in January under 30 degrees?",
    // "Which months in 2023 had the most rain?",
    // "What is the average temperature for February 14th?",
    // "What was the average temperature for today over the last 5 years?"
  ]

  const clearMessages = async () => {

  await fetch(`${root_url}/clear/`, {   
      method: "GET",
      headers: {
        "Access-Control-Allow-Origin": "*" 
      },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      setMessages([])
    })
    .catch((error) => console.log(error));
  }

  const sendMessage = async (form) => {

    // Don't let form refresh page after submit
    form.preventDefault();
    const formData = new FormData(form.target);
    const formJSON = Object.fromEntries(formData.entries());


    setInput("")
    // Update state of messages to include user's prompt
    setMessages([
      ...messages, 
      {'role': 'user', 'content': formJSON['message']}
    ])

    setIsLoading(true);

    await fetch(`${root_url}/message/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json", 
        "Access-Control-Allow-Origin": "*" 
      },
      body: 
      JSON.stringify({
        "sid": sid, 
        "message": formJSON['message']
      })
    })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);

      setIsLoading(false);
      // Update state of messages to include user's prompt, and assistant response
      setMessages([
        ...messages, 
        {'role': 'user', 'content': formJSON['message']},
        data['message']
      ]);

      // Update logs to include new message log
      setLogs([...logs, data['log']])
    })
    .catch((error) => {
      console.log(error);
      setIsLoading(false);

      // Display error message
      const errMsg = {'role': 'assistant', 'content': "I'm sorry, I encountered an error answering this question."}
      setMessages([
        ...messages, 
        {'role': 'user', 'content': formJSON['message']},
        errMsg
      ]);
    });
  }

  return (
    <div className='w-screen h-screen flex flex-row'>
      {/* Left panel */}
      <div className='h-full w-1/4 flex flex-col justify-between p-5 bg-zinc-950 border-zinc-800'>

        {/* Example prompts */}
        <div className='flex flex-col mx-auto px-5 mt-10 text-white h-1/2 overflow-y-scroll'>
          <p className='text-md font-bold mb-2 sticky top-0 bg-zinc-950 py-2'>Example prompts</p>
          {exPrompts && exPrompts.map((prompt) => 
            <p
            onClick={() => setInput(prompt)}
            className='text-sm py-2 hover:text-white hover:cursor-pointer text-neutral-300' key={prompt}>{prompt}</p>
          )}
        </div>

        {/* Buttons */}
        <div className='flex flex-col space-y-8'>
          {/* 'Show logs' button */}
          <button
            onClick={() => setToggleLogs(!toggleLogs)}
            className='mx-auto w-4/5 py-3 bg-zinc-900 bg-opacity-80 text-blue-600 rounded-lg hover:bg-opacity-90'
            >Display logs
          </button>
          {/* 'Add checkpoint' button */}
          <button
            onClick={() => {
              if(!isLoading && messages.length > 0 && !checkpoints.includes(messages.slice(-1)[0]['timestamp']) )
                setCheckpoints([...checkpoints, messages.slice(-1)[0]['timestamp']])
            }}
            className='mx-auto w-4/5 py-3 bg-zinc-900 bg-opacity-80 text-green-500 rounded-lg hover:bg-opacity-90'
            >Add checkpoint
          </button>

          {/* 'Clear conversation' button */}
          <button
              onClick={() => clearMessages()} 
              className='mx-auto w-4/5 py-3 bg-zinc-900 bg-opacity-80 text-red-500 rounded-lg hover:bg-opacity-90'>Clear conversation
          </button>
        </div>

      </div>

      {/* Main card */}
      <div className='h-full w-3/4 flex flex-col justify-between bg-zinc-900 p-5'>
        {/* Message panel */}
        <div className='h-full w-3/4 mx-auto overflow-scroll flex flex-col text-white pb-5'>

        {messages && messages.map(({i, role, content, timestamp}) => 
            <div className='flex flex-col' key={i}>
              <Message role={role} content={content} timestamp={timestamp}/>

              {checkpoints && checkpoints.includes(timestamp) && 
              <div className='w-full mt-4 flex flex-row justify-center'>
                  <div className='my-auto w-full h-1 border-b border-zinc-500'></div>
                  <p className='text-zinc-500 text-sm font-bold mx-3'>{checkpoints.indexOf(timestamp) + 1}</p>
                <div className='my-auto w-full h-1 border-b border-zinc-500'></div>
              </div>}
            </div>)}
        {isLoading &&
          // Animated loading circles
          <div class='flex space-x-2 py-4 justify-start'>
            <span class='sr-only'>Loading...</span>
            <div class='h-2 w-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.3s]'></div>
            <div class='h-2 w-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.15s]'></div>
            <div class='h-2 w-2 bg-zinc-400 rounded-full animate-bounce'></div>
          </div>}
        </div>

        {/* Chat input */}
        <div className='sticky bottom-0 w-3/4 mx-auto z-10 pt-5 bg-zinc-900'>
          <form onSubmit={sendMessage} className='flex flex-row justify-between rounded-xl p-1 bg-zinc-900 outline outline-zinc-700'>
            <input 
                type="text" 
                name="message"
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className='w-full px-3 py-3 rounded-md bg-zinc-900 text-white focus:outline-none'
                placeholder='Enter a prompt...'
                autoComplete='off'
              >
              </input>
              <button type="submit" 
                className={input.length > 0  
                  ? 'px-2 py-1 m-2 text-zinc-900 bg-zinc-400 rounded-md' 
                  : 'px-2 py-1 m-2 text-zinc-900 bg-zinc-700 hover:bg-zinc-400 rounded-md' }>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="3" stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
                </svg>
              </button>
          </form>
        </div>
      </div>

      {/* Log panel */}
      {toggleLogs && 
      <div className='h-full w-1/2 flex flex-col justify-start space-y-4 pb-5 overflow-y-scroll bg-zinc-950 border-zinc-800'>
        <div className='sticky top-0 bg-zinc-950 p-5'>
          <p className='text-white font-bold text-2xl'>Chat logs</p>
        </div>
        {logs && logs.map(({i, timestamp, prompt, query, result, response}) => 
        // Log
        <div className='flex flex-col px-5'>
          <MessageLog timestamp={timestamp} prompt={prompt} query={query} result={result} response={response} key={i}/>
        
          {checkpoints && checkpoints.includes(timestamp) && 
            <div className='w-full mt-4 flex flex-row justify-center'>
              <div className='my-auto w-full h-1 border-b border-zinc-500'></div>
              <p className='text-zinc-500 text-sm font-bold mx-3'>{checkpoints.indexOf(timestamp) + 1}</p>
            <div className='my-auto w-full h-1 border-b border-zinc-500'></div>
          </div>}
        </div>)}

        {/* 'Clear logs' button */}
        {logs && logs.length > 0 ? 
        <button 
          onClick={() => setLogs([])}
          className='mx-auto w-4/5 py-3 bg-zinc-900 bg-opacity-80 text-red-500 rounded-lg hover:bg-opacity-90'
          >Clear
        </button>
        : 
        // Message if nothing logged yet
        <p className='px-5 text-neutral-300'>
          <span className='font-bold hover:cursor-pointer' onClick={() => {
            inputRef.current.focus();
            setToggleLogs(!toggleLogs);
            }}>Start a conversation</span> for chat logs to appear here.
          </p>}
      </div>}
    
    </div>
  );
}

export default App;
