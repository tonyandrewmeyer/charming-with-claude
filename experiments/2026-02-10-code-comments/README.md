Prompt:

```
Write a Python script that uses a Genetic Algorithm to evolve a string of text until it matches a target phrase (e.g., 'Evolution in Python'). The script should include functions for creating a random population, calculating fitness scores, selecting parents, and performing crossover and mutation.
```

Claude Code (Opus 4.6), no instructions:

```python
import random
import string

TARGET = "Evolution in Python"
POPULATION_SIZE = 200
MUTATION_RATE = 0.02
GENE_POOL = string.ascii_letters + string.digits + string.punctuation + " "


def random_individual(length):
    return "".join(random.choice(GENE_POOL) for _ in range(length))


def create_population(size, length):
    return [random_individual(length) for _ in range(size)]


def fitness(individual, target):
    return sum(a == b for a, b in zip(individual, target))


def select_parent(population, fitnesses):
    """Tournament selection: pick 3 random individuals, return the fittest."""
    contestants = random.sample(list(zip(population, fitnesses)), k=3)
    return max(contestants, key=lambda x: x[1])[0]


def crossover(parent_a, parent_b):
    """Single-point crossover."""
    point = random.randint(1, len(parent_a) - 1)
    return parent_a[:point] + parent_b[point:]


def mutate(individual, rate):
    chars = list(individual)
    for i in range(len(chars)):
        if random.random() < rate:
            chars[i] = random.choice(GENE_POOL)
    return "".join(chars)


def evolve(target=TARGET, population_size=POPULATION_SIZE, mutation_rate=MUTATION_RATE):
    length = len(target)
    population = create_population(population_size, length)
    generation = 0

    while True:
        fitnesses = [fitness(ind, target) for ind in population]

        best_fitness = max(fitnesses)
        best_individual = population[fitnesses.index(best_fitness)]

        if generation % 20 == 0 or best_fitness == length:
            print(f"Gen {generation:>4} | Best: {best_individual!r} | Fitness: {best_fitness}/{length}")

        if best_fitness == length:
            print(f"\nTarget matched in {generation} generations.")
            return best_individual, generation

        next_population = []

        # Elitism: carry the best individual forward unchanged
        next_population.append(best_individual)

        while len(next_population) < population_size:
            parent_a = select_parent(population, fitnesses)
            parent_b = select_parent(population, fitnesses)
            child = crossover(parent_a, parent_b)
            child = mutate(child, mutation_rate)
            next_population.append(child)

        population = next_population
        generation += 1


if __name__ == "__main__":
    evolve()
```

Copilot CLI (Sonnet 4.5), no instructions

```python
#!/usr/bin/env python3
"""
Genetic Algorithm for Text Evolution
Evolves a population of random strings to match a target phrase.
"""

import random
import string


class GeneticAlgorithm:
    def __init__(self, target, population_size=100, mutation_rate=0.01):
        """
        Initialize the Genetic Algorithm.
        
        Args:
            target (str): The target phrase to evolve towards
            population_size (int): Number of individuals in the population
            mutation_rate (float): Probability of mutation (0-1)
        """
        self.target = target
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.genes = string.ascii_letters + string.punctuation + ' '
        self.generation = 0
        
    def create_individual(self):
        """Create a random individual (string) of the same length as target."""
        return ''.join(random.choice(self.genes) for _ in range(len(self.target)))
    
    def create_population(self):
        """Create initial population of random individuals."""
        return [self.create_individual() for _ in range(self.population_size)]
    
    def calculate_fitness(self, individual):
        """
        Calculate fitness score for an individual.
        Higher score means closer to target.
        
        Args:
            individual (str): The string to evaluate
            
        Returns:
            int: Number of matching characters in correct positions
        """
        return sum(1 for i, char in enumerate(individual) if char == self.target[i])
    
    def select_parent(self, population, fitness_scores):
        """
        Select a parent using tournament selection.
        
        Args:
            population (list): List of individuals
            fitness_scores (list): Corresponding fitness scores
            
        Returns:
            str: Selected parent individual
        """
        tournament_size = 5
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_individuals = [(population[i], fitness_scores[i]) for i in tournament_indices]
        winner = max(tournament_individuals, key=lambda x: x[1])
        return winner[0]
    
    def crossover(self, parent1, parent2):
        """
        Perform single-point crossover between two parents.
        
        Args:
            parent1 (str): First parent
            parent2 (str): Second parent
            
        Returns:
            str: Offspring created from both parents
        """
        crossover_point = random.randint(1, len(self.target) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]
    
    def mutate(self, individual):
        """
        Mutate an individual by randomly changing characters.
        
        Args:
            individual (str): The individual to mutate
            
        Returns:
            str: Mutated individual
        """
        individual_list = list(individual)
        for i in range(len(individual_list)):
            if random.random() < self.mutation_rate:
                individual_list[i] = random.choice(self.genes)
        return ''.join(individual_list)
    
    def evolve(self, max_generations=10000, verbose=True):
        """
        Run the genetic algorithm evolution process.
        
        Args:
            max_generations (int): Maximum number of generations
            verbose (bool): Whether to print progress
            
        Returns:
            tuple: (best_individual, generation_found)
        """
        population = self.create_population()
        
        for generation in range(max_generations):
            self.generation = generation
            
            # Calculate fitness for all individuals
            fitness_scores = [self.calculate_fitness(ind) for ind in population]
            
            # Find best individual
            best_index = fitness_scores.index(max(fitness_scores))
            best_individual = population[best_index]
            best_fitness = fitness_scores[best_index]
            
            # Print progress
            if verbose and (generation % 100 == 0 or best_fitness == len(self.target)):
                print(f"Generation {generation:4d} | Best: '{best_individual}' | Fitness: {best_fitness}/{len(self.target)}")
            
            # Check if target is reached
            if best_individual == self.target:
                if verbose:
                    print(f"\n🎉 Target reached in generation {generation}!")
                return best_individual, generation
            
            # Create new population
            new_population = []
            
            # Elitism: keep the best individual
            new_population.append(best_individual)
            
            # Generate rest of population
            while len(new_population) < self.population_size:
                parent1 = self.select_parent(population, fitness_scores)
                parent2 = self.select_parent(population, fitness_scores)
                
                offspring = self.crossover(parent1, parent2)
                offspring = self.mutate(offspring)
                
                new_population.append(offspring)
            
            population = new_population
        
        # If max generations reached without finding target
        fitness_scores = [self.calculate_fitness(ind) for ind in population]
        best_index = fitness_scores.index(max(fitness_scores))
        if verbose:
            print(f"\n⚠️  Max generations ({max_generations}) reached without finding exact match.")
        return population[best_index], max_generations


def main():
    """Main function to demonstrate the Genetic Algorithm."""
    target_phrase = "Evolution in Python"
    
    print("=" * 60)
    print("Genetic Algorithm: Text Evolution")
    print("=" * 60)
    print(f"Target phrase: '{target_phrase}'")
    print(f"Length: {len(target_phrase)} characters")
    print("=" * 60)
    print()
    
    # Create and run the genetic algorithm
    ga = GeneticAlgorithm(
        target=target_phrase,
        population_size=200,
        mutation_rate=0.01
    )
    
    best_solution, generations = ga.evolve(max_generations=10000, verbose=True)
    
    print()
    print("=" * 60)
    print("Final Results:")
    print(f"Best solution: '{best_solution}'")
    print(f"Generations: {generations}")
    print(f"Match: {best_solution == target_phrase}")
    print("=" * 60)


if __name__ == "__main__":
    main()
```


Claude, with:

```
Comments explain the *why*, not the *how*. If you add a comment, you may need to simplify the code instead.
```

```python
import random
import string

TARGET = "Evolution in Python"
POPULATION_SIZE = 200
MUTATION_RATE = 0.02
GENES = string.ascii_letters + string.digits + string.punctuation + " "


def random_gene():
    return random.choice(GENES)


def create_individual(length):
    return "".join(random_gene() for _ in range(length))


def create_population(size, length):
    return [create_individual(length) for _ in range(size)]


def fitness(individual, target):
    return sum(1 for a, b in zip(individual, target) if a == b) / len(target)


def select_parent(population, fitnesses):
    """Tournament selection: pick 3 random individuals, return the fittest."""
    contestants = random.sample(list(zip(population, fitnesses)), k=3)
    return max(contestants, key=lambda x: x[1])[0]


def crossover(parent1, parent2):
    """Single-point crossover."""
    point = random.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:]


def mutate(individual, rate):
    return "".join(
        random_gene() if random.random() < rate else ch
        for ch in individual
    )


def evolve(target=TARGET, pop_size=POPULATION_SIZE, mutation_rate=MUTATION_RATE):
    length = len(target)
    population = create_population(pop_size, length)
    generation = 0

    while True:
        fitnesses = [fitness(ind, target) for ind in population]
        best_idx = fitnesses.index(max(fitnesses))
        best = population[best_idx]
        best_fit = fitnesses[best_idx]

        print(f"Gen {generation:4d} | Fitness: {best_fit:.2%} | Best: {best!r}")

        if best == target:
            print(f"\nTarget matched in {generation} generations!")
            return best, generation

        # Build next generation, keeping the best individual (elitism)
        next_population = [best]

        for _ in range(pop_size - 1):
            p1 = select_parent(population, fitnesses)
            p2 = select_parent(population, fitnesses)
            child = crossover(p1, p2)
            child = mutate(child, mutation_rate)
            next_population.append(child)

        population = next_population
        generation += 1


if __name__ == "__main__":
    evolve()
```

Copilot:

```python 
#!/usr/bin/env python3
"""
Genetic Algorithm for Text Evolution
Evolves random strings to match a target phrase.
"""

import random
import string


TARGET = "Evolution in Python"
POPULATION_SIZE = 200
MUTATION_RATE = 0.01
ELITE_SIZE = 20


def create_individual(length):
    """Generate a random string of given length."""
    chars = string.ascii_letters + string.punctuation + ' '
    return ''.join(random.choice(chars) for _ in range(length))


def create_population(size, length):
    """Create initial population of random strings."""
    return [create_individual(length) for _ in range(size)]


def calculate_fitness(individual, target):
    """Calculate fitness score (number of matching characters)."""
    return sum(1 for i, c in enumerate(individual) if c == target[i])


def select_parents(population, target, num_parents):
    """Select parents using tournament selection."""
    parents = []
    for _ in range(num_parents):
        tournament = random.sample(population, 5)
        winner = max(tournament, key=lambda ind: calculate_fitness(ind, target))
        parents.append(winner)
    return parents


def crossover(parent1, parent2):
    """Perform single-point crossover between two parents."""
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2


def mutate(individual, mutation_rate):
    """Mutate individual by randomly changing characters."""
    chars = string.ascii_letters + string.punctuation + ' '
    individual_list = list(individual)
    for i in range(len(individual_list)):
        if random.random() < mutation_rate:
            individual_list[i] = random.choice(chars)
    return ''.join(individual_list)


def evolve_population(population, target, elite_size, mutation_rate):
    """Create next generation through selection, crossover, and mutation."""
    fitness_scores = [(ind, calculate_fitness(ind, target)) for ind in population]
    fitness_scores.sort(key=lambda x: x[1], reverse=True)
    
    elite = [ind for ind, _ in fitness_scores[:elite_size]]
    
    new_population = elite.copy()
    
    while len(new_population) < len(population):
        parents = select_parents(population, target, 2)
        child1, child2 = crossover(parents[0], parents[1])
        
        child1 = mutate(child1, mutation_rate)
        child2 = mutate(child2, mutation_rate)
        
        new_population.extend([child1, child2])
    
    return new_population[:len(population)]


def run_genetic_algorithm(target, population_size, mutation_rate, elite_size):
    """Run the genetic algorithm until target is reached."""
    population = create_population(population_size, len(target))
    generation = 0
    
    while True:
        fitness_scores = [calculate_fitness(ind, target) for ind in population]
        best_fitness = max(fitness_scores)
        best_individual = population[fitness_scores.index(best_fitness)]
        
        if generation % 10 == 0:
            print(f"Generation {generation:4d} | Best: '{best_individual}' | Fitness: {best_fitness}/{len(target)}")
        
        if best_individual == target:
            print(f"\n✓ Target reached in generation {generation}!")
            print(f"  Final string: '{best_individual}'")
            return best_individual, generation
        
        population = evolve_population(population, target, elite_size, mutation_rate)
        generation += 1


if __name__ == "__main__":
    print("=" * 60)
    print("Genetic Algorithm: Text Evolution")
    print("=" * 60)
    print(f"Target phrase: '{TARGET}'")
    print(f"Population size: {POPULATION_SIZE}")
    print(f"Mutation rate: {MUTATION_RATE}")
    print(f"Elite size: {ELITE_SIZE}")
    print("=" * 60)
    print()
    
    result, generations = run_genetic_algorithm(
        TARGET, 
        POPULATION_SIZE, 
        MUTATION_RATE, 
        ELITE_SIZE
    )
    
    print(f"\nCompleted successfully after {generations} generations!")
```

Claude with copilot collections:

```python
import random
import string

# --- Configuration ---
TARGET = "Evolution in Python"
POPULATION_SIZE = 200
MUTATION_RATE = 0.02
ELITE_COUNT = 2
GENE_POOL = string.ascii_letters + string.digits + string.punctuation + " "


def random_individual(length):
    """Create a random string of the given length from the gene pool."""
    return "".join(random.choice(GENE_POOL) for _ in range(length))


def create_population(size, length):
    """Create an initial population of random individuals."""
    return [random_individual(length) for _ in range(size)]


def fitness(individual, target):
    """Calculate fitness as the number of characters that match the target."""
    return sum(a == b for a, b in zip(individual, target))


def select_parent(population, fitnesses):
    """Select a parent via tournament selection (k=3)."""
    contestants = random.sample(list(zip(population, fitnesses)), k=3)
    return max(contestants, key=lambda x: x[1])[0]


def crossover(parent_a, parent_b):
    """Single-point crossover between two parents."""
    point = random.randint(1, len(parent_a) - 1)
    return parent_a[:point] + parent_b[point:]


def mutate(individual, rate):
    """Randomly replace characters based on the mutation rate."""
    chars = list(individual)
    for i in range(len(chars)):
        if random.random() < rate:
            chars[i] = random.choice(GENE_POOL)
    return "".join(chars)


def evolve(target=TARGET):
    """Run the genetic algorithm until the target string is matched."""
    length = len(target)
    population = create_population(POPULATION_SIZE, length)
    generation = 0

    while True:
        fitnesses = [fitness(ind, target) for ind in population]
        best_idx = fitnesses.index(max(fitnesses))
        best = population[best_idx]
        best_fit = fitnesses[best_idx]

        print(f"Gen {generation:4d} | Best: {best!r:30s} | Fitness: {best_fit}/{length}")

        if best == target:
            print(f"\nTarget matched in generation {generation}!")
            return best, generation

        # Elitism: carry the top individuals forward unchanged
        ranked = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
        next_population = [ind for ind, _ in ranked[:ELITE_COUNT]]

        # Fill the rest of the next generation
        while len(next_population) < POPULATION_SIZE:
            parent_a = select_parent(population, fitnesses)
            parent_b = select_parent(population, fitnesses)
            child = crossover(parent_a, parent_b)
            child = mutate(child, MUTATION_RATE)
            next_population.append(child)

        population = next_population
        generation += 1


if __name__ == "__main__":
    evolve()
```
copilot :

```python
#!/usr/bin/env python3
"""
Genetic Algorithm for String Evolution
Evolves a random population of strings until they match a target phrase.
"""

import random
import string


TARGET = "Evolution in Python"
POPULATION_SIZE = 200
MUTATION_RATE = 0.01
TOURNAMENT_SIZE = 5


def create_individual(length):
    """Generate a random string of specified length."""
    chars = string.ascii_letters + string.punctuation + ' '
    return ''.join(random.choice(chars) for _ in range(length))


def create_population(size, individual_length):
    """Create initial population of random strings."""
    return [create_individual(individual_length) for _ in range(size)]


def calculate_fitness(individual, target):
    """
    Calculate fitness score based on matching characters.
    Higher score = closer to target.
    """
    return sum(1 for ind_char, tar_char in zip(individual, target) if ind_char == tar_char)


def select_parent(population, target):
    """
    Tournament selection: pick best individual from random subset.
    Ensures diversity while favoring fitter individuals.
    """
    tournament = random.sample(population, TOURNAMENT_SIZE)
    return max(tournament, key=lambda ind: calculate_fitness(ind, target))


def crossover(parent1, parent2):
    """
    Single-point crossover: combine two parents at random split point.
    Child inherits beginning from parent1, end from parent2.
    """
    split_point = random.randint(1, len(parent1) - 1)
    return parent1[:split_point] + parent2[split_point:]


def mutate(individual, mutation_rate):
    """
    Randomly change characters based on mutation rate.
    Introduces diversity to prevent premature convergence.
    """
    chars = string.ascii_letters + string.punctuation + ' '
    individual_list = list(individual)
    
    for i in range(len(individual_list)):
        if random.random() < mutation_rate:
            individual_list[i] = random.choice(chars)
    
    return ''.join(individual_list)


def evolve(target, population_size=POPULATION_SIZE, mutation_rate=MUTATION_RATE):
    """
    Main evolution loop.
    Evolves population until an individual matches the target.
    """
    population = create_population(population_size, len(target))
    generation = 0
    max_fitness = len(target)
    
    print(f"Target: '{target}'")
    print(f"Population Size: {population_size}")
    print(f"Mutation Rate: {mutation_rate}")
    print(f"Tournament Size: {TOURNAMENT_SIZE}")
    print("-" * 60)
    
    while True:
        generation += 1
        
        fitness_scores = [(ind, calculate_fitness(ind, target)) for ind in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        best_individual, best_fitness = fitness_scores[0]
        
        if generation == 1 or generation % 10 == 0 or best_fitness == max_fitness:
            avg_fitness = sum(score for _, score in fitness_scores) / len(fitness_scores)
            print(f"Generation {generation:4d} | Best: '{best_individual}' | "
                  f"Fitness: {best_fitness}/{max_fitness} | Avg: {avg_fitness:.2f}")
        
        if best_fitness == max_fitness:
            print("-" * 60)
            print(f"SUCCESS! Target reached in {generation} generations!")
            return best_individual, generation
        
        new_population = []
        
        # Elitism: keep the best individual
        new_population.append(best_individual)
        
        while len(new_population) < population_size:
            parent1 = select_parent(population, target)
            parent2 = select_parent(population, target)
            
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            
            new_population.append(child)
        
        population = new_population


def main():
    """Run the genetic algorithm with default or custom parameters."""
    try:
        result, generations = evolve(TARGET)
        print(f"\nFinal Result: '{result}'")
        print(f"Total Generations: {generations}")
    except KeyboardInterrupt:
        print("\n\nEvolution interrupted by user.")


if __name__ == "__main__":
    main()
```
