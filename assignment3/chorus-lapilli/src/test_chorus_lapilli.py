#!/usr/bin/env python3
'''Simple test harness for Chorus Lapilli.

Extend the TestChorusLapilli class to add your own tests.
'''
import os
import sys
import argparse
import subprocess
import unittest
import urllib.request

class TestChorusLapilli(unittest.TestCase):
    '''Integration testing for Chorus Lapilli

    This class handles the entire react start up, testing, and take down
    process. Feel free to modify it to suit your needs.
    '''

    # ========================== [USEFUL CONSTANTS] ===========================

    # React default startup address
    REACT_HOST_ADDR = 'http://localhost:3000'

    # XPATH query used to find Chorus Lapilli board tiles
    BOARD_TILE_XPATH = '//button[contains(@class, \'square\')]'

    # Sets of symbol classes - each string contains all valid characters
    # for that particular symbol
    SYMBOL_BLANK = ''
    SYMBOL_X = 'Xx'
    SYMBOL_O = '0Oo'

    # ======================== [SETUP/TEARDOWN HOOKS] =========================

    @classmethod
    def setUpClass(cls):
        '''This function runs before testing occurs.

        Bring up the web app and configure Selenium
        '''

        env = dict(os.environ)
        env.update({
            # Prevent React from starting its own browser window
            'BROWSER': 'none',
            # Disable SSL warnings for Legacy NodeJS
            'NODE_OPTIONS': '--openssl-legacy-provider'
        })

        # if npm install has never been run, install dependencies
        if not os.path.isfile('package-lock.json'):
            subprocess.run(['npm', 'install'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           env=env,
                           check=True)

        # Await Webserver Start
        cls.react = subprocess.Popen(['node',
                                      'node_modules/react-scripts/scripts/'
                                      'start.js'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL,
                                     env=env)
        for _ in cls.react.stdout:
            try:
                with urllib.request.urlopen(cls.REACT_HOST_ADDR):
                    break

            except IOError:
                pass

            # Ensure React does not terminate early
            if cls.react.poll() is not None:
                raise OSError('React terminated before test')

        # Configure the Selenium webdriver
        cls.driver = Browser()
        cls.driver.get(cls.REACT_HOST_ADDR)
        cls.driver.implicitly_wait(0.5)

    @classmethod
    def tearDownClass(cls):
        '''This function runs after all testing have run.

        Terminate React and take down the Selenium webdriver.
        '''
        cls.react.terminate()
        cls.react.wait()
        cls.driver.quit()

    def setUp(self):
        '''This function runs before every test.

        Refresh the browser so we get a new board.
        '''
        self.driver.refresh()

    def tearDown(self):
        '''This function runs after every test.

        Not needed, but feel free to add stuff here.
        '''

    # ========================== [HELPER FUNCTIONS] ===========================

    def assertBoardEmpty(self, tiles):
        '''Checks if all board tiles are empty.

        Arguments:
          tiles: List[WebElement] - a board consisting of 9 buttons elements
        Raises:
          AssertionError - if board is not empty
        '''
        if len(tiles) != 9:
            raise AssertionError('tiles is not a 3x3 grid')
        for i, tile in enumerate(tiles):
            if tile.text.strip():
                raise AssertionError(f'tile {i} is not empty: '
                                     f'\'{tile.text}\'')

    def assertTileIs(self, tile, symbol_set):
        '''Checks if a tile contains a symbol from the symbol set.

        Arguments:
          tile: WebElement - the button element to check
          symbol_set: str - a string containing all the valid symbols
        Raises:
          AssertionError - if tile is not in the symbol set
        '''
        if symbol_set is None:
            return
        if symbol_set == self.SYMBOL_BLANK:
            name = 'BLANK'
        elif symbol_set == self.SYMBOL_X:
            name = 'X'
        elif symbol_set == self.SYMBOL_O:
            name = 'O'
        else:
            name = 'in symbol_set'
        text = tile.text.strip()
        if ((symbol_set == self.SYMBOL_BLANK and text)
                or (symbol_set != self.SYMBOL_BLANK and not text)
                or text not in symbol_set):
            raise AssertionError(f'tile is not {name}: \'{tile.text}\'')

    # =========================== [ADD YOUR TESTS HERE] ===========================

    def test_new_board_empty(self):
        '''Check if a new game always starts with an empty board.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertBoardEmpty(tiles)

    def test_button_click(self):
        '''Check if clicking the top-left button adds an X.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertTileIs(tiles[0], self.SYMBOL_BLANK)
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_alternate_turns(self):
        '''Check that players alternate turns and the correct symbol is placed.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # First move by X
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        # Second move by O
        tiles[1].click()
        self.assertTileIs(tiles[1], self.SYMBOL_O)
        # Third move by X
        tiles[2].click()
        self.assertTileIs(tiles[2], self.SYMBOL_X)

    def test_click_on_occupied_square(self):
        '''Check that clicking on an occupied square does not change its value.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # First move by X
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        # Try clicking on the same square again
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        # Second move by O
        tiles[1].click()
        self.assertTileIs(tiles[1], self.SYMBOL_O)

    def test_no_moves_after_win(self):
        '''Check that after a player wins, no further moves are allowed.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # Simulate moves leading to a win for X
        # Placement Phase
        tiles[0].click()  # X
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        tiles[3].click()  # O
        self.assertTileIs(tiles[3], self.SYMBOL_O)
        tiles[1].click()  # X
        self.assertTileIs(tiles[1], self.SYMBOL_X)
        tiles[4].click()  # O
        self.assertTileIs(tiles[4], self.SYMBOL_O)
        tiles[2].click()  # X - X should win here
        self.assertTileIs(tiles[2], self.SYMBOL_X)

        # Attempt to make an additional move by O
        tiles[5].click()  # O tries to move
        # Since the game is over, the tile should remain empty
        self.assertTileIs(tiles[5], self.SYMBOL_BLANK)

        # Verify that the board did not change
        self.assertTileIs(tiles[5], self.SYMBOL_BLANK)
        # Ensure that the winner is still X
        # (If your game displays a status message, you could check it here)

    def test_move_to_non_adjacent_square(self):
        '''Check that moving a piece to a non-adjacent square is not allowed.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # Placement Phase
        tiles[0].click()  # X
        tiles[3].click()  # O
        tiles[1].click()  # X
        tiles[4].click()  # O
        tiles[2].click()  # X
        tiles[5].click()  # O

        # Movement Phase starts
        # X tries to move a piece from position 0 to position 8 (non-adjacent)
        tiles[0].click()  # Select piece at 0
        tiles[8].click()  # Try to move to 8 (should not be allowed)
        # Check that tile[8] is still blank
        self.assertTileIs(tiles[8], self.SYMBOL_BLANK)
        # Check that tile[0] is still X
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_vacate_center_square_rule(self):
        '''Check that a player with a piece in the center must vacate it or win.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # Placement Phase
        tiles[0].click()  # X
        tiles[4].click()  # O (center)
        tiles[1].click()  # X
        tiles[3].click()  # O
        tiles[2].click()  # X
        tiles[5].click()  # O

        # Movement Phase starts
        # O has a piece in the center and must either win or vacate it
        # Attempt to move a non-center piece (should not be allowed)
        tiles[3].click()  # Select piece at 3 (non-center)
        tiles[6].click()  # Try to move to 6
        # Should not be allowed; tile[6] should remain empty
        self.assertTileIs(tiles[6], self.SYMBOL_BLANK)
        # The selected piece should remain at position 3
        self.assertTileIs(tiles[3], self.SYMBOL_O)

        # O must move the center piece
        tiles[4].click()  # Select center piece
        # Attempt to move it to an adjacent square
        tiles[7].click()  # Move to 7
        self.assertTileIs(tiles[4], self.SYMBOL_BLANK)
        self.assertTileIs(tiles[7], self.SYMBOL_O)

    # ================= [DO NOT MAKE ANY CHANGES BELOW THIS LINE] =================

if __name__ != '__main__':
    from selenium.webdriver import Firefox as Browser
    from selenium.webdriver.common.by import By
else:
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Chorus Lapilli Tester')
    parser.add_argument('-b',
                        '--browser',
                        action='store',
                        metavar='name',
                        choices=['firefox', 'chrome', 'safari'],
                        default='firefox',
                        help='the browser to run tests with')
    parser.add_argument('-c',
                        '--change-dir',
                        action='store',
                        metavar='dir',
                        default=None,
                        help=('change the working directory before running '
                              'tests'))

    # Change the working directory
    options = parser.parse_args(sys.argv[1:])
    # Import different browser drivers based on user selection
    try:
        if options.browser == 'firefox':
            from selenium.webdriver import Firefox as Browser
        elif options.browser == 'chrome':
            from selenium.webdriver import Chrome as Browser
        else:
            from selenium.webdriver import Safari as Browser
        from selenium.webdriver.common.by import By
    except ImportError as err:
        print('[Error]',
              err, '\n\n'
              'Please refer to the Selenium documentation on installing the '
              'webdriver:\n'
              'https://www.selenium.dev/documentation/webdriver/'
              'getting_started/',
              file=sys.stderr)
        sys.exit(1)

    if options.change_dir:
        try:
            os.chdir(options.change_dir)
        except OSError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

    if not os.path.isfile('package.json'):
        print('Invalid directory: cannot find \'package.json\'',
              file=sys.stderr)
        sys.exit(1)

    tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestChorusLapilli)
    unittest.TextTestRunner().run(tests)
