#!/usr/bin/python

from optparse import OptionParser
import iperf3
import graphyte
import sys

def parse_options():
  parser = OptionParser()
  parser.add_option("-t", "--target-host", dest="host", help="iperf3 target host", default='127.0.0.1')
  parser.add_option("-p", "--target-port", dest="port", help="iperf3 target port", default=5201)
  parser.add_option("-d", "--duration", dest="duration", help="iperf3 test duration", default=10)
  parser.add_option("-g", "--graphite-host", dest="graphite_host", help="graphite host (with port)", default='127.0.0.1:2003')
  parser.add_option("-x", "--graphite-prefix", dest="graphite_prefix", help="graphite prefix for the metrics", default='')
  parser.add_option("-l", "--metric-list" , dest="requested_metrics", help="List of metrics to be pulled from the iperf3 object and setn to graphite", default='sent_Mbps,received_Mbps')
  return parser.parse_args()

def perform_test(duration, target_hostname, target_port):
  try:
    client = iperf3.Client()
    client.duration = duration
    client.server_hostname = target_hostname
    client.port = target_port
    return client.run()
  except OSError as e:
    print("ERROR: iperf3 may not be installed", file=sys.stderr)
    sys.exit(1)


def send_to_graphite(graphite_host, prefix, metrics_list):
  graphyte.init(graphite_host, prefix=prefix)
  for metric in metrics_list:
    graphyte.send(metric['name'], metric['value'])
  return True

def build_metrics_list(iperf3_results, requested_metrics):
  metrics_list = []
  for metric in requested_metrics:
    try:
      value = getattr(iperf3_results, metric)
      metrics_list.append({
        'name': metric,
        'value': value
      })
    except AttributeError as e:
      print(f"ERROR: metric {metric} could not be pulled")
      pass
  return metrics_list

def main():
  (options, args) = parse_options()
  result = perform_test(options.duration, options.host, options.port)
  metrics_list = build_metrics_list(result, options.requested_metrics.split(","))
  send_to_graphite(options.graphite_host, options.graphite_prefix, metrics_list)


if __name__ == "__main__":
  main()
