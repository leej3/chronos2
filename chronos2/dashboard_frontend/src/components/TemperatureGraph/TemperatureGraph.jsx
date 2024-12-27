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
import { API_BASE_URL } from '../../utils/constant';
import { getCharData } from '../../api/getCharData';

const TemperatureGraph = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getCharData();
        const result = await response.data;

        // Map the data to the correct format for the chart
        const mappedData = result.map((entry) => {
          const date = new Date(entry.date);
          const formattedDate = date.toLocaleString(); 

          return {
            name: formattedDate, 
            inlet: entry['column-2'],
            outlet: entry['column-1'],
          };
        });
        setData(mappedData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const [date, time] = label.split(', '); 
      const formattedTime = time.slice(0, 5); 
  
      return (
        <div className="custom-tooltip" style={{ backgroundColor: '#333645', padding: '10px', borderRadius: '5px' }}>
          <p style={{ color: '#fff' }}><strong>Time: </strong>{date}, {formattedTime}</p> {/* Hiển thị ngày và giờ */}
          <p style={{ color: '#ffca28' }}><strong>Inlet: </strong>{payload[0].value}°C</p>
          <p style={{ color: '#ff7043' }}><strong>Outlet: </strong>{payload[1].value}°C</p>
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

  const downloadLogs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chart_data`);
      const blob = await response.blob(); // Get the response as a Blob

      // Create a link element
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'chart_data'; // Set the file name (you can add the correct extension here if known, e.g., 'chart_data.csv')

      // Append the link to the body and trigger the download
      document.body.appendChild(link);
      link.click();

      // Remove the link after download
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
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
              tick={{ fill: '#dddddd', fontSize: 12 }}
              tickFormatter={(tick) => {
                const [date, time] = tick.split(', ');
                return time.slice(0, 5); 
              }}
              angle={-45} 
              textAnchor="end" 
            >
              <Label
                value="Time"
                offset={10} 
                position="insideBottom"
                fill="#dddddd"
                style={{ textAnchor: 'middle', fontSize: 14 }}
              />
            </XAxis>
            <YAxis 
              domain={[30, 90]} 
              stroke="#dddddd"
              tick={{ fill: '#dddddd', fontSize: 12 }}
            >
              <Label
                value="Temperature (°C)"
                angle={-90}
                position="insideLeft"
                fill="#dddddd"
                style={{ textAnchor: 'middle', fontSize: 14 }}
              />
            </YAxis>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ color: '#dddddd' }}
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
        <button
          className="download-button"
          style={{ marginLeft: '20px' }}
          onClick={downloadLogs}
        >
          Download logs json
        </button>
      </div>
    </div>
  );
};

export default TemperatureGraph;
