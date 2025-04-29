import React from 'react';

function Bottom3Careers({ skills }) {
  const bottom3 = skills.slice(-3); // from bottom 3

  return (
    <div>
      <h2>Bottom 3 Career Outlooks</h2>
      <ul>
        {bottom3.map(skill => (
          <li key={skill.id}>{skill.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default Bottom3Careers;
