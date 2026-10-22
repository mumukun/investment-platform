import fs from 'node:fs';
import assert from 'node:assert/strict';
import { fiveMinuteFlowPoints } from '../../../../investment-research-dashboard/src/components/sectorCapitalFlowGeometry.ts';
const folder = new URL('./', import.meta.url);
const trend = JSON.parse(fs.readFileSync(new URL('trend-replay.json', folder), 'utf8'));
const rows = trend.series.map(row => {
  const points = fiveMinuteFlowPoints(trend.times, row.values);
  for (const [time, value] of points) {
    if (value !== null) assert.equal(value, row.values[trend.times.indexOf(time)]);
  }
  assert(points.some(([time,value]) => time === '13:00' && value === null));
  return {name:row.name, originalSamples:row.values.filter(v=>v!==null).length, trendPoints:points.filter(([,v])=>v!==null).length, preservedActualTimesAndAmounts:true};
});
fs.writeFileSync(new URL('geometry-report.json',folder),JSON.stringify({rows,networkRequests:0},null,2)+'\n');
console.log(JSON.stringify(rows[0]));
