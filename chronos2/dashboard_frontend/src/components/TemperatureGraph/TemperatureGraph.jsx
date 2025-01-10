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
import { formatNumber } from '../../utils/tranform';

const TemperatureGraph = () => {
  const [data, setData] = useState([]);
  const [interval, setInterval] = useState(4);
  const [chartHeight, setChartHeight] = useState(600); // Default chart height

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
            hour12: true,
          });

          return {
            name: formattedDate,
            inlet: formatNumber(entry['column-2'], 0),
            outlet: formatNumber(entry['column-1'], 0),
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
        setChartHeight(400); 
      } else {
        setInterval(4);
        setChartHeight(600); 
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
      return (
        <div
          className="custom-tooltip"
          style={{
            backgroundColor: '#333645',
            padding: '8px 12px', 
            borderRadius: '5px',
            fontSize: '12px', 
            maxWidth: '200px', 
            color: '#fff', 
          }}
        >
          <p style={{ fontSize: '12px', margin: '5px 0' }}>
            <strong>Time: </strong>{label}
          </p>
          <p style={{ fontSize: '12px', margin: '5px 0', color: '#ffca28' }}>
            <strong>Inlet: </strong>{payload[0].value}°F
          </p>
          <p style={{ fontSize: '12px', margin: '5px 0', color: '#ff7043' }}>
            <strong>Outlet: </strong>{payload[1].value}°F
          </p>
        </div>
      );
    }
    return null;
  };

  const downloadCSV = () => {
    const header = ['Date', 'Inlet Temperature (°F)', 'Outlet Temperature (°F)'];
    const rows = data.map((entry) => [
      entry.name,
      entry.inlet,
      entry.outlet,
    ]);

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += header.join(',') + '\n';

    rows.forEach((row) => {
      csvContent += row.join(',') + '\n';
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'temperature_data.csv');
    link.click();
  };

  return (
    <div className="graph-container">
      <div className="graphbody">
        <h3>Inlet/Outlet Temperature History</h3>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <LineChart data={data}>
            <CartesianGrid stroke="#4c5c77" strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              stroke="#dddddd"
              tick={{ fill: '#dddddd', fontSize: 12, fontWeight: 'bold' }}
              tickFormatter={(tick, index) => {
                if (index === 0) {
                  return '';
                }
                const [date, time] = tick.split(', ');
                return time;
              }}
              angle={0}
              textAnchor="middle"
              interval={interval}
            />
            <YAxis
              domain={[30, 90]}
              stroke="#dddddd"
              tick={{ fill: '#dddddd', fontSize: 12, fontWeight: 'bold' }}
              tickFormatter={(tick) => Math.round(tick)} 
            >
              <Label
                value="Temperature (°F)"
                angle={-90}
                position="insideLeft"
                fill="#dddddd"
                style={{ textAnchor: 'middle', fontSize: 18 }}
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
              dot={{ r: 3 }} 
            />
            <Line
              type="monotone"
              dataKey="outlet"
              stroke="#ff7043"
              strokeWidth={2} 
              dot={{ r: 3 }} 
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
