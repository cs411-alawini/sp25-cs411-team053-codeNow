import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Top5Careers from './components/CareerList/Top5Careers';
import Bottom3Careers from './components/CareerList/Bottom3Careers';
import UserPrefCareers from './components/CareerList/UserPrefCareers';
import './App.css';

function App() {
  /*const [skills, setSkills] = useState([
    { id: 1, name: 'React' },
    { id: 2, name: 'Node.js' },
    { id: 3, name: 'Python' },
    { id: 4, name: 'SQL' },
    { id: 5, name: 'Django' },
    { id: 6, name: 'AWS' },
    { id: 7, name: 'Docker' },
  ]);*/
  
  const [skills, setSkills] = useState([]);

  useEffect(() => {
    fetch('/api/skills/')
      .then(response => response.json())
      .then(data => setSkills(data))
      .catch(error => console.log(error));
  }, []); 

  return (
    <div>
       <h1>All Skills</h1>
       <ul>
         {skills.map(skill => (
           <li key={skill.id}>{skill.name}</li>
         ))}
       </ul>
     </div>
  );
}

export default App;
