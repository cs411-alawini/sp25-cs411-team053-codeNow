import React, { useEffect, useState } from 'react';

function App() {
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
