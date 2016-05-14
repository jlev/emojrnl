var Emojrnl = (function () {
  var emojrnl = {};

  emojrnl.login = function(hashid) {
    // TBD
  };

  emojrnl.chart = function(entry_list) {
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 320 - margin.left - margin.right,
    height = 250 - margin.top - margin.bottom;

    // merge each entry.txt into array
    var txt_merge = _.pluck(entry_list, 'txt').join('');
    // count histogram of each symbol
    var hist = _(Array.from(txt_merge)).countBy(function(char) { return char });
    var data = d3.entries(hist).sort(function(a,b) {return d3.descending(a.value, b.value)});
    // TODO, limit to ten entries

    var x = d3.scale.ordinal()
      .rangeRoundBands([0, width], .5);
    var y = d3.scale.ordinal()
       .rangeRoundPoints([height, 0], 1);
    x.domain(data.map(function(d) { return d.key; }));
    y.domain([1, d3.max(data, function(d) { return d.value; })]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .outerTickSize([0]); // don't show end ticks
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .outerTickSize([0])
        .tickFormat(['']); // hide tick values

    var svg = d3.select(".chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

    if ($('html').hasClass('ios')) {
      d3.selectAll(".x.axis .tick text")
        .attr('class', 'emoji')
        .attr('y', function(d) { return 0; })
        .attr("transform", "scale(2)");
    }

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    var bar = svg.selectAll(".chart > g")
        .data(data)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d, i) { return "translate(" + x(d.key) + ", 0)"; });

    bar.append("rect")
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.value); })
        .attr("height", function(d) { return height - y(d.value); });

    bar.append("text")
      .attr("y", function(d) { return y(d.value); })
      .attr("dy", "1.5em")
      .attr("dx", x.rangeBand()/2)
      .attr("text-anchor", "middle")
      .text(function(d) { return d.value; });
  }

  emojrnl.render = function(data) {
    console.log(data);
    // render #stats
    $('#phone').html(data.phone.replace(/(\d{1})(\d{3})(\d{3})(\d{4})/, '$2-$3-$4')); // TODO, parse e164
    $('#member_since').html(moment(data.created_at, moment.ISO_8601).format('LL'));
    
    // render #chart
    emojrnl.chart(data.entries);

    // render #badges
    $('#total_emoji').html(_.reduce(data.entries, function(sum, e){
      return (sum + Array.from(e.txt).length); // need to convert string to array to count unicode char correctly
    }, 0));
    $('#total_entries').html(data.entries.length);
    $('#longest_streak').html(data.longest_streak.length)

    // render #today
    var latest_entry = data.entries[0];
    var latest_moment = moment(latest_entry.created_at, moment.ISO_8601)
    $('#today .entry .time').html(latest_moment.format('LT'));
    $('#today .entry .day').html(latest_moment.format('dddd'));
    $('#today .entry .date').html(latest_moment.format('MMMM Do'));
    $('#today .entry .txt').html(latest_entry.txt);

    // render #calendar
    _.each(data.entries, function(entry) {
      $('ul#journal').append('<li class="entry">'+
        '<span class="date">'+moment(entry.created_at, moment.ISO_8601).format('dd LT')+'</span>'+
        '<span class="txt emoji">'+entry.txt+'</span>'+
        '</li>'
      );
    });
  };

  return emojrnl;
}());