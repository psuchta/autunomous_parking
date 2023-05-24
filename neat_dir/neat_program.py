from cars.autonomous_controlled_car import AutonomousControlledCar
from cars.neat_controlled_car import NeatControlledCar
from base_program import BaseProgram
from genetic.genetic_helper import GeneticHelper
from genetic.genetic_program import GeneticProgram
import pygame
import os
import neat
import random
import numpy
import visualize

class NeatProgram(GeneticProgram):

  def __init__(self):
    seed = 1086
    random.seed(seed)
    numpy.random.seed(seed)

    BaseProgram.__init__(self)
    self.genetic_helper = GeneticHelper()

    self.history_file_path="neat_dir/plots/plot_history.csv"
    self.gen_num = 1
    self.history_df = []

  def add_game_objects(self):
    car = None
    BaseProgram.add_game_objects(self)
    random_coordinates = self.get_random_location()
    for idx in range(30):
      car = NeatControlledCar(random_coordinates[0], random_coordinates[1], self.screen, self)
      self.add_car(car)

  def set_genomes(self, genomes, config):
    for idx, genome in enumerate(genomes):
      self.steerable_cars[idx].set_chromosome(genome[1], config)

  def run_generation(self, genomes, config):
    self.set_genomes(genomes, config)
    random_coordinates = self.get_random_location()
    [car.reset(random_coordinates[0], random_coordinates[1]) for car in self.steerable_cars]
    # Call parent's class function
    GeneticProgram.run_generation(self, self.gen_num)

    self.genetic_helper.calculate_fitness_in_cars(self.steerable_cars, self.parking_slot)
    
    self.gen_num += 1
    self.add_generation_to_history(self.gen_num, self.steerable_cars)

    # Copy car's fitnes to NEAT genome 
    self.set_fitness_to_NEAT_genome(self.steerable_cars)

  def set_fitness_to_NEAT_genome(self, car_population):
    for car in car_population:
      car.chromosome.fitness = car.fitness


  def run_neat(self, config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(self.run_generation, 200)

    # Draw own statistics
    self.draw_history_plot()

    # Neat statistics
    # visualize.plot_stats(stats, ylog=False, view=False, filename="fitness.svg")
    # visualize.draw_net(config, winner, True)

  def run(self):
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'settings.txt')
    self.run_neat(config_path)

