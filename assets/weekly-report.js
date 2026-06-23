(function () {
  const report = document.querySelector(".week-report");
  if (!report) return;

  const summaryUrl = report.getAttribute("data-summary-url");
  const topicLabel = report.getAttribute("data-topic-label") || "Survey topic";
  const participantSectionLabel = report.getAttribute("data-participant-section-label") || "Participant-vote determined";
  const tableBody = document.querySelector("#item-overview-table tbody");
  const cardGrid = document.querySelector("#item-card-grid");
  const ballotBody = document.querySelector("#ballot-table tbody");
  const nextBallotBody = document.querySelector("#next-ballot-table tbody");

  const formatNumber = (value) => {
    if (value === null || value === undefined) return "n/a";
    return Number.isInteger(value) ? String(value) : Number(value).toFixed(1);
  };

  const pct = (count, total) => {
    if (!total) return 0;
    return Math.max(0, Math.min(100, (count / total) * 100));
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "0.0";
    return Number(value).toFixed(1);
  };

  const formatDoubtDogma = (item) => {
    const metric = item.doubt_dogma;
    if (!metric) return "n/a";
    return `${metric.non_endpoint_count}:${metric.endpoint_count}`;
  };

  const createDoubtDogmaRatio = (item) => {
    const metric = item.doubt_dogma;
    if (!metric) {
      const fallback = document.createElement("span");
      fallback.textContent = "n/a";
      return fallback;
    }
    const ratio = document.createElement("span");
    ratio.className = "doubt-dogma-ratio";
    ratio.setAttribute(
      "aria-label",
      `${metric.non_endpoint_count} non-endpoint responses to ${metric.endpoint_count} endpoint responses`
    );

    const doubt = document.createElement("span");
    doubt.className = "doubt-count";
    doubt.textContent = metric.non_endpoint_count;

    const separator = document.createElement("span");
    separator.className = "ratio-separator";
    separator.setAttribute("aria-hidden", "true");
    separator.textContent = ":";

    const dogma = document.createElement("span");
    dogma.className = "dogma-count";
    dogma.textContent = metric.endpoint_count;

    ratio.append(doubt, separator, dogma);
    return ratio;
  };

  const sanitizeSparklineValues = (values) => {
    if (!Array.isArray(values) || values.length !== 10) return null;
    return values.map((value) => Math.max(0, Math.min(100, Number(value) || 0)));
  };

  const displayValuesFromCounts = (item) => {
    const counts = item.distribution && item.distribution.simple_counts;
    const n = Number(item.n);
    if (!Array.isArray(counts) || counts.length !== 10 || !n) return null;
    const padded = [0, ...counts, 0];
    return counts.map((_, index) => {
      const value = ((padded[index] * 0.03 + padded[index + 1] + padded[index + 2] * 0.03) / n) * 100;
      return Math.max(0, Math.min(100, value));
    });
  };

  const sparklineValues = (item) => {
    const values = item.distribution && item.distribution.display_percentages;
    return sanitizeSparklineValues(values) || displayValuesFromCounts(item);
  };

  const sparklineBinLabel = (item, index) => {
    const cuts = item.distribution && item.distribution.cut_points;
    if (!Array.isArray(cuts) || cuts.length < index + 2) return `Bin ${index + 1}`;
    return `${cuts[index]}-${cuts[index + 1]}`;
  };

  const sparklineColorClass = (index) => {
    if (index <= 2) return "low";
    if (index <= 6) return "middle";
    return "high";
  };

  const sparklineMax = () => 100;

  const createBand = (item) => {
    const band = document.createElement("div");
    band.className = "band-bar";
    band.setAttribute("aria-label", `Low ${item.bands.low}, middle ${item.bands.middle}, high ${item.bands.high}`);
    [
      ["low", "Disagreeing"],
      ["middle", "Mixed"],
      ["high", "Agreeing"]
    ].forEach(([key, label]) => {
      const segment = document.createElement("span");
      segment.className = `band-segment ${key}`;
      segment.style.width = `${pct(item.bands[key], item.n)}%`;
      segment.title = `${label}: ${item.bands[key]} of ${item.n}`;
      band.appendChild(segment);
    });
    return band;
  };

  const createSparkline = (item, scaleMax) => {
    const values = sparklineValues(item);
    if (!values) return createBand(item);

    const chart = document.createElement("div");
    chart.className = "sparkline-chart";
    chart.setAttribute("role", "img");
    chart.setAttribute(
      "aria-label",
      `Observed 10-bin distribution with light neighbor smoothing for Q${item.number}; 100 percent guide line shown at the top of the fixed 0 to 100 display scale: ${values.map((value, index) => `${sparklineBinLabel(item, index)} ${formatPercent(value)}%`).join("; ")}`
    );

    values.forEach((value, index) => {
      const bar = document.createElement("span");
      bar.className = `sparkline-bar ${sparklineColorClass(index)}`;
      const height = value > 0 ? (value / scaleMax) * 100 : 0;
      bar.style.height = `${height}%`;
      bar.style.minHeight = value > 0 ? "3px" : "0";
      bar.title = `${sparklineBinLabel(item, index)}: ${formatPercent(value)}%`;
      chart.appendChild(bar);
    });

    return chart;
  };

  const itemClass = (item) => {
    const lowShare = item.bands.low / item.n;
    const highShare = item.bands.high / item.n;
    if (highShare >= 0.85 && item.median >= 90) return "Consensus";
    if (lowShare >= 0.2 && highShare >= 0.2) return "Divided";
    if (item.standard_deviation >= 35) return "Wide spread";
    return "Leaning high";
  };

  const sectionLabel = (section) => {
    if (section === "participant_vote_seeded" || section === "participant_vote_determined") {
      return participantSectionLabel;
    }
    return topicLabel;
  };

  const renderTable = (items, scaleMax) => {
    tableBody.textContent = "";
    items.forEach((item) => {
      const row = document.createElement("tr");

      const itemCell = document.createElement("td");
      const itemTitle = document.createElement("strong");
      itemTitle.textContent = `Q${item.number}. ${item.short_label}`;
      const itemText = document.createElement("span");
      itemText.textContent = item.text;
      itemCell.appendChild(itemTitle);
      itemCell.appendChild(itemText);
      row.appendChild(itemCell);

      const meanCell = document.createElement("td");
      meanCell.textContent = formatNumber(item.mean);
      row.appendChild(meanCell);

      const iqrCell = document.createElement("td");
      iqrCell.textContent = `${formatNumber(item.q1)}-${formatNumber(item.q3)}`;
      row.appendChild(iqrCell);

      const doubtDogmaCell = document.createElement("td");
      doubtDogmaCell.className = "doubt-dogma-cell";
      doubtDogmaCell.appendChild(createDoubtDogmaRatio(item));
      if (item.doubt_dogma) {
        doubtDogmaCell.title = `${item.doubt_dogma.non_endpoint_count} non-endpoint responses / ${item.doubt_dogma.endpoint_count} endpoint responses`;
      }
      row.appendChild(doubtDogmaCell);

      const barCell = document.createElement("td");
      barCell.className = "sparkline-cell";
      barCell.appendChild(createSparkline(item, scaleMax));
      row.appendChild(barCell);

      tableBody.appendChild(row);
    });
  };

  const renderCards = (items, scaleMax) => {
    cardGrid.textContent = "";
    items.forEach((item) => {
      const card = document.createElement("article");
      card.className = "item-result-card";

      const meta = document.createElement("div");
      meta.className = "item-card-meta";
      meta.innerHTML = `<span>Q${item.number}</span><span>${sectionLabel(item.section)}</span><span>${itemClass(item)}</span>`;

      const heading = document.createElement("h3");
      heading.textContent = item.short_label;

      const text = document.createElement("p");
      text.textContent = `➘ ${item.text}`;

      const statGrid = document.createElement("dl");
      statGrid.className = "item-stat-grid";
      const iqrLabel = `
        <span class="metric-popover">
          <button class="metric-popover-trigger" type="button">IQR Range</button>
          <span class="metric-popover-panel" role="note">
            <strong>Interquartile range</strong>
            The middle 50% of responses, from the 25th percentile to the 75th percentile. A range such as 49-92 means half of respondents landed between 49 and 92.
          </span>
        </span>
      `;
      const doubtDogmaLabel = `
        <span class="metric-popover">
          <button class="metric-popover-trigger" type="button">Doubt/Dogma</button>
          <span class="metric-popover-panel" role="note">
            <strong>Doubt/Dogma ratio</strong>
            Shown as n:m. The green first number is non-endpoint responses, from 1 to 99; the red second number is endpoint responses, exactly 0 or 100. Higher first numbers mean respondents avoided absolutes more often.
          </span>
        </span>
      `;
      [
        ["Mean", item.mean],
        ["IQR Range", `${formatNumber(item.q1)}-${formatNumber(item.q3)}`],
        ["Doubt/Dogma", formatDoubtDogma(item)],
        ["SD", item.standard_deviation]
      ].forEach(([label, value]) => {
        const wrap = document.createElement("div");
        const dt = document.createElement("dt");
        const dd = document.createElement("dd");
        if (label === "IQR Range") {
          dt.innerHTML = iqrLabel;
        } else if (label === "Doubt/Dogma") {
          dt.innerHTML = doubtDogmaLabel;
        } else {
          dt.textContent = label;
        }
        if (label === "Doubt/Dogma") {
          dd.appendChild(createDoubtDogmaRatio(item));
        } else {
          dd.textContent = typeof value === "number" ? formatNumber(value) : value;
        }
        wrap.appendChild(dt);
        wrap.appendChild(dd);
        statGrid.appendChild(wrap);
      });

      const barWrap = document.createElement("div");
      barWrap.className = "sparkline-wrap";
      const legend = document.createElement("p");
      legend.className = "sparkline-legend";
      legend.textContent = "Observed 10-bin distribution";
      barWrap.appendChild(legend);
      barWrap.appendChild(createSparkline(item, scaleMax));

      card.appendChild(meta);
      card.appendChild(heading);
      card.appendChild(text);
      card.appendChild(statGrid);
      card.appendChild(barWrap);
      cardGrid.appendChild(card);
    });
  };

  const renderBallot = (ballot) => {
    ballotBody.textContent = "";
    ballot.items.forEach((item) => {
      const row = document.createElement("tr");
      const rankCell = document.createElement("td");
      rankCell.textContent = item.rank;
      const textCell = document.createElement("td");
      textCell.textContent = item.text;
      const scoreCell = document.createElement("td");
      scoreCell.textContent = formatNumber(item.score);
      row.appendChild(rankCell);
      row.appendChild(textCell);
      row.appendChild(scoreCell);
      ballotBody.appendChild(row);
    });
  };

  const sourceLabel = (source) => {
    if (!source) return "Candidate";
    if (source === "participant_suggestion") return "Participant suggestion";
    const carryover = String(source).match(/^week_(\d+)_ballot_carryover$/);
    if (carryover) return `Week ${Number(carryover[1])} carryover`;
    return String(source).replace(/_/g, " ");
  };

  const renderNextBallot = (draft) => {
    if (!nextBallotBody || !draft || !Array.isArray(draft.items)) return;
    nextBallotBody.textContent = "";
    draft.items.forEach((item) => {
      const row = document.createElement("tr");
      const rankCell = document.createElement("td");
      rankCell.textContent = item.rank;
      const textCell = document.createElement("td");
      textCell.textContent = item.text;
      const sourceCell = document.createElement("td");
      sourceCell.textContent = sourceLabel(item.source);
      row.appendChild(rankCell);
      row.appendChild(textCell);
      row.appendChild(sourceCell);
      nextBallotBody.appendChild(row);
    });
  };

  fetch(summaryUrl, { cache: "no-cache" })
    .then((response) => {
      if (!response.ok) throw new Error("Summary file not available.");
      return response.json();
    })
    .then((summary) => {
      const scaleMax = sparklineMax(summary.items);
      renderTable(summary.items, scaleMax);
      renderCards(summary.items, scaleMax);
      renderBallot(summary.ballot);
      renderNextBallot(summary.next_week_ballot_draft);
    })
    .catch(() => {
      if (tableBody) {
        tableBody.innerHTML = "<tr><td colspan=\"5\">The aggregate summary file could not be loaded. Please use the public JSON link below.</td></tr>";
      }
      if (ballotBody) {
        ballotBody.innerHTML = "<tr><td colspan=\"3\">The aggregate summary file could not be loaded.</td></tr>";
      }
      if (nextBallotBody) {
        nextBallotBody.innerHTML = "<tr><td colspan=\"3\">The aggregate summary file could not be loaded.</td></tr>";
      }
    });
})();
