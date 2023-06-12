import cProfile

from .Typoceros import Typo


# Define the function to be profiled
def my_function():
	LONG_TEXT = '''Metaphysical solipsism is a variety of solipsism. Based on a philosophy of subjective idealism, metaphysical solipsists maintain that the self is the only existing reality and that all other realities, including the external world and other persons, are representations of that self, and have no independent existence.[citation needed] There are several versions of metaphysical solipsism, such as Caspar Hare's egocentric presentism (or perspectival realism), in which other people are conscious, but their experiences are simply not present.'''
	LONG_TEXT = '''Hi, How are you?'''
	t = Typo(LONG_TEXT)
	t.spaces
	return t

# Start the profiler
profiler = cProfile.Profile()
profiler.enable()

# Call the function to be profiled
t = my_function()

# Stop the profiler
profiler.disable()

# Get the statistics
stats = profiler.getstats()

# Sort the statistics by total time spent in each function
stats.sort(key=lambda stat: stat.totaltime, reverse=True)

# Print the sorted statistics in a formatted way
for stat in stats:
    print(f"Function: {stat.code}")
    print(f"Total time spent in the function: {stat.totaltime:.2f} seconds")
    print(f"Total number of calls to the function: {stat.ncalls}")
    print(f"Time spent per call: {stat.totaltime / stat.ncalls:.2f} seconds")
    print("------")
