import { useState } from "react";
import { sid, root_url } from "../App";


export default function MessageLog({timestamp, prompt, query, result, response}){


    const [toggleFeedback, setToggleFeedback] = useState(false)
    const [feedbackInput, setFeedbackInput] = useState("")
    const [feedbackSelected, setFeedbackSelected] = useState("")
    const [commentFill, setCommentFill] = useState(false)


    const updateFeedback = async (timestamp, attribute, feedback_type, feedback_content) => {
        
        await fetch(`${root_url}/feedback/update`, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "*" 
            },
            body: 
            JSON.stringify({
                  "sid": sid,
                  "timestamp": timestamp,
                  "attribute": attribute,
                  "type": feedback_type,
                  "content": feedback_content
              })
          })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
  
            // Set selected feedback to one that was clicked
            if (feedback_type === "feedback")
              setFeedbackSelected(feedback_content);
  
          })
          .catch((error) => console.log(error));
        }

    return(
        <div className='flex flex-col space-y-2 text-white text-sm'>
            {/* Timestamp */}
            <p className='font-bold'>{timestamp}</p>
            {/* Prompt */}
            <p className='text-cyan-300'>{prompt['content']}</p>
            {/* Content if SQL*/}
            {query && query['content'] && query['content']['sql'] && <p className='text-blue-400'>{query['content']['sql']}</p>}

            {/* Query result */}
            {result && <p className='text-emerald-300'>{Array.isArray(result) && result.flat().length > 1 ? result.flat().join('; ') : result}</p>}
            
            {/* Query Feedback */}
            {query && <div className='w-full flex flex-row py-2 bg-zinc-950 space-x-1'>
                <p className='text-zinc-500 text-sm my-auto'>How does this look?</p>
                {/* Thumbs up */}
                <div 
                    className='bg-zinc-950 p-2 my-auto rounded-full hover:cursor-pointer hover:bg-zinc-900'
                    onClick={() => updateFeedback(timestamp, "sql", "feedback", "Correct")}
                >
                    {feedbackSelected === "Correct" 
                    ? // Filled thumbs up
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-zinc-500">
                        <path d="M7.493 18.5c-.425 0-.82-.236-.975-.632A7.48 7.48 0 0 1 6 15.125c0-1.75.599-3.358 1.602-4.634.151-.192.373-.309.6-.397.473-.183.89-.514 1.212-.924a9.042 9.042 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75A.75.75 0 0 1 15 2a2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.605.729H14.23c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 0 0-1.423-.23h-.777ZM2.331 10.727a11.969 11.969 0 0 0-.831 4.398 12 12 0 0 0 .52 3.507C2.28 19.482 3.105 20 3.994 20H4.9c.445 0 .72-.498.523-.898a8.963 8.963 0 0 1-.924-3.977c0-1.708.476-3.305 1.302-4.666.245-.403-.028-.959-.5-.959H4.25c-.832 0-1.612.453-1.918 1.227Z" />
                    </svg>
                    : // Outlined 
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6 text-zinc-500">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 0 0-1.423-.23H5.904m10.598-9.75H14.25M5.904 18.5c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 0 1-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 9.953 4.167 9.5 5 9.5h1.053c.472 0 .745.556.5.96a8.958 8.958 0 0 0-1.302 4.665c0 1.194.232 2.333.654 3.375Z" />
                    </svg>}
                </div>
                {/* Thumbs down */}
                <div 
                    className='bg-zinc-950 p-2 my-auto rounded-full hover:cursor-pointer hover:bg-zinc-900'
                    onClick={() => updateFeedback(timestamp, "sql", "feedback", "Incorrect")}
                >
                    {feedbackSelected === "Incorrect" 
                    ? // Filled thumbs down
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-zinc-500">
                        <path d="M15.73 5.5h1.035A7.465 7.465 0 0 1 18 9.625a7.465 7.465 0 0 1-1.235 4.125h-.148c-.806 0-1.534.446-2.031 1.08a9.04 9.04 0 0 1-2.861 2.4c-.723.384-1.35.956-1.653 1.715a4.499 4.499 0 0 0-.322 1.672v.633A.75.75 0 0 1 9 22a2.25 2.25 0 0 1-2.25-2.25c0-1.152.26-2.243.723-3.218.266-.558-.107-1.282-.725-1.282H3.622c-1.026 0-1.945-.694-2.054-1.715A12.137 12.137 0 0 1 1.5 12.25c0-2.848.992-5.464 2.649-7.521C4.537 4.247 5.136 4 5.754 4H9.77a4.5 4.5 0 0 1 1.423.23l3.114 1.04a4.5 4.5 0 0 0 1.423.23ZM21.669 14.023c.536-1.362.831-2.845.831-4.398 0-1.22-.182-2.398-.52-3.507-.26-.85-1.084-1.368-1.973-1.368H19.1c-.445 0-.72.498-.523.898.591 1.2.924 2.55.924 3.977a8.958 8.958 0 0 1-1.302 4.666c-.245.403.028.959.5.959h1.053c.832 0 1.612-.453 1.918-1.227Z" />
                    </svg>
                    : // Outlined
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6 text-zinc-500">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M7.498 15.25H4.372c-1.026 0-1.945-.694-2.054-1.715a12.137 12.137 0 0 1-.068-1.285c0-2.848.992-5.464 2.649-7.521C5.287 4.247 5.886 4 6.504 4h4.016a4.5 4.5 0 0 1 1.423.23l3.114 1.04a4.5 4.5 0 0 0 1.423.23h1.294M7.498 15.25c.618 0 .991.724.725 1.282A7.471 7.471 0 0 0 7.5 19.75 2.25 2.25 0 0 0 9.75 22a.75.75 0 0 0 .75-.75v-.633c0-.573.11-1.14.322-1.672.304-.76.93-1.33 1.653-1.715a9.04 9.04 0 0 0 2.86-2.4c.498-.634 1.226-1.08 2.032-1.08h.384m-10.253 1.5H9.7m8.075-9.75c.01.05.027.1.05.148.593 1.2.925 2.55.925 3.977 0 1.487-.36 2.89-.999 4.125m.023-8.25c-.076-.365.183-.75.575-.75h.908c.889 0 1.713.518 1.972 1.368.339 1.11.521 2.287.521 3.507 0 1.553-.295 3.036-.831 4.398-.306.774-1.086 1.227-1.918 1.227h-1.053c-.472 0-.745-.556-.5-.96a8.95 8.95 0 0 0 .303-.54" />
                    </svg>}
                </div>
                {/* Toggle comment */}
                <div 
                    className='bg-zinc-950 p-2 my-auto rounded-full hover:cursor-pointer hover:bg-zinc-900'
                    onClick={() => setToggleFeedback(!toggleFeedback)}
                >
                {commentFill ? 
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-zinc-500">
                        <path fillRule="evenodd" d="M4.848 2.771A49.144 49.144 0 0 1 12 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 0 1-3.476.383.39.39 0 0 0-.297.17l-2.755 4.133a.75.75 0 0 1-1.248 0l-2.755-4.133a.39.39 0 0 0-.297-.17 48.9 48.9 0 0 1-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97ZM6.75 8.25a.75.75 0 0 1 .75-.75h9a.75.75 0 0 1 0 1.5h-9a.75.75 0 0 1-.75-.75Zm.75 2.25a.75.75 0 0 0 0 1.5H12a.75.75 0 0 0 0-1.5H7.5Z" clip-rule="evenodd" />
                    </svg>
                    : 
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6 text-zinc-500">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                    </svg>}
                </div>
                {toggleFeedback && 
                    <form 
                    onSubmit={(form) => {
                        form.preventDefault();
                        updateFeedback(timestamp, "sql", "comment", feedbackInput);
                        setCommentFill(true);
                        setFeedbackInput("");
                    }} 
                    className='group/input-wrapper flex flex-row w-1/3 justify-between rounded-xl p-2 -m-1 bg-zinc-950 hover:bg-zinc-900'>
                    <input               
                        type="text" 
                        name="message"
                        value={feedbackInput}
                        onChange={(e) => setFeedbackInput(e.target.value)}
                        className='w-full text-sm px-2 py-1 rounded-xl bg-zinc-950 group-hover/input-wrapper:bg-zinc-900 text-zinc-400 focus:outline-none'
                        placeholder='Add Comment...'
                        autoComplete='off'>
                    </input>
                        <button type="submit" className='px-1 py-1 m-1 text-zinc-950 bg-zinc-700 hover:bg-zinc-500 rounded-md'>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" className="w-4 h-4">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
                            </svg>
                        </button>
                    </form>}
                </div>}

            {/* NL response */}
            {response['content'] && response['content']['text'] && <p className='text-red-400'>{response['content']['text']}</p>}
            {response['content'] && response['content']['plot'] && <p className='text-orange-500'>{`Visualization: ${response['content']['plot']}`}</p>}
    </div>
    );
}