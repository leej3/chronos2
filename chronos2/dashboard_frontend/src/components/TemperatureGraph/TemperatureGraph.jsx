import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
} from 'recharts';
import './TemperatureGraph.css';
import { getCharData } from '../../api/getCharData';
import {formatNumber} from "../../utils/tranform"

const TemperatureGraph = () => {
  const [data, setData] = useState([]);
  const [interval, setInterval] = useState(4); 

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getCharData();
        const result = await response.data;

        const mappedData = result.map((entry) => {
          const date = new Date(entry.date);
          const formattedDate = date.toLocaleString('en-US', {
            timeZone: 'America/Chicago',
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
          });

          return {
            name: formattedDate,
            inlet: formatNumber(entry['column-2']),
            outlet: formatNumber(entry['column-1']),
          };
        });

        setData(mappedData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 120000); 

    const handleResize = () => {
      if (window.innerWidth < 768) {
        setInterval(8); 
      } else {
        setInterval(4); 
      }
    };

    handleResize(); 
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const [date, time] = label.split(', ');
      return (
        <div className="custom-tooltip" style={{ backgroundColor: '#333645', padding: '10px', borderRadius: '5px' }}>
          <p style={{ color: '#fff' }}><strong>Time: </strong>{label}</p>
          <p style={{ color: '#ffca28' }}><strong>Inlet: </strong>{payload[0].value}°F</p>
          <p style={{ color: '#ff7043' }}><strong>Outlet: </strong>{payload[1].value}°F</p>
        </div>
      );
    }
    return null;
  };

  const convertToCSV = (arr) => {
    const array = [Object.keys(arr[0])].concat(arr);
    return array.map((it) => Object.values(it).toString()).join('\n');
  };

  const downloadCSV = () => {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'temperature_log.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="graph-container">
      <div className="graphbody">
        <h3>Inlet/Outlet Temperature History</h3>
        <ResponsiveContainer width="100%" height={600}>
          <LineChart data={data}>
            <CartesianGrid stroke="#4c5c77" strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              stroke="#dddddd"
              tick={{ fill: '#dddddd', fontSize: 14, fontWeight: 'bold' }}
              tickFormatter={(tick, index) => {
                if (index === 0) {
                  return "";
                }
                const [date, time] = tick.split(', ');
                return time; 
              }}
              angle={0} 
              textAnchor="middle" 
              interval={interval} 
            >
            </XAxis>
            <YAxis 
              domain={[30, 90]} 
              stroke="#dddddd"
              tick={{ fill: '#dddddd', fontSize: 14, fontWeight: 'bold' }}
            >
              <Label
                value="Temperature (°F)"
                angle={-90}
                position="insideLeft"
                fill="#dddddd"
                style={{ textAnchor: 'middle', fontSize: 20 }}
              />
            </YAxis>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ fill: '#dddddd' }}
            />
            <Line
              type="monotone"
              dataKey="inlet"
              stroke="#ffca28"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="outlet"
              stroke="#ff7043"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
        <button className="download-button" onClick={downloadCSV}>
          Download logs csv
        </button>
      </div>
    </div>
  );
};

export default TemperatureGraph;
